import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as s3 from 'aws-cdk-lib/aws-s3';
import { ACCOUNT_ID, LAMBDA_PYTHON_RUNTIME, REGION, Stage } from './constants';

import * as path from 'path';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as sfn from 'aws-cdk-lib/aws-stepfunctions';
import * as tasks from 'aws-cdk-lib/aws-stepfunctions-tasks';
import * as iam from 'aws-cdk-lib/aws-iam';

interface ConnectorsProps extends cdk.StackProps {
  stage: Stage,
}

export class ConnectorsStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: ConnectorsProps) {
    super(scope, id, props);

    const bucket = new s3.Bucket(this, `EpdRawDataBucket`, {
      bucketName: `epd-raw-data-${props.stage}-${props.env?.region}`,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      encryption: s3.BucketEncryption.S3_MANAGED,
      enforceSSL: true,
      versioned: false,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
    })


    const requestsLayer = new lambda.LayerVersion(this, 'RequestsLayer', {
      code: lambda.Code.fromAsset(path.join(__dirname, '../../connectors/lambda_layers/lambda_layer.zip')),
      compatibleRuntimes: [LAMBDA_PYTHON_RUNTIME],
    });

    const getAllEpdInfosLambda = new lambda.Function(this, 'GetAllEpdInfosEcoPlatformLambda', {
      runtime: LAMBDA_PYTHON_RUNTIME,
      handler: 'get_all_epd_infos.lambda_handler',
      code: lambda.Code.fromAsset(path.join(__dirname, '../../connectors/ecoplatform/lambda')),
      timeout: cdk.Duration.minutes(5),
      layers: [requestsLayer],
      environment: {
        "BUCKET_NAME": bucket.bucketName
      }
    });

    const getEpdDataLambda = new lambda.Function(this, 'GetEpdDataEcoPlatformLambda', {
      runtime: LAMBDA_PYTHON_RUNTIME,
      handler: 'get_epd_data.lambda_handler',
      code: lambda.Code.fromAsset(path.join(__dirname, '../../connectors/ecoplatform/lambda')),
      timeout: cdk.Duration.minutes(15),
      layers: [requestsLayer],
      environment: {
        "BUCKET_NAME": bucket.bucketName
      }
    });

    const s3Policy = new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: [
        's3:ListBucket',
        's3:GetObject',
        's3:PutObject',
        's3:DeleteObject',
      ],
      resources: [
        `arn:aws:s3:::${bucket.bucketName}`,
        `arn:aws:s3:::${bucket.bucketName}/*`,
      ],
    });

    const secretsManagerPolicy = new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: ['ssm:GetParameter'],
      resources: [`arn:aws:ssm:${REGION}:${ACCOUNT_ID}:parameter/etl/ECOPLATFORM_TOKEN`],
    });

    getAllEpdInfosLambda.addToRolePolicy(s3Policy);
    getAllEpdInfosLambda.addToRolePolicy(secretsManagerPolicy);
    getEpdDataLambda.addToRolePolicy(s3Policy);
    getEpdDataLambda.addToRolePolicy(secretsManagerPolicy);

    // Step Function Tasks
    const getAllEpdInfosTask = new tasks.LambdaInvoke(this, 'Get All EPD Infos', {
      lambdaFunction: getAllEpdInfosLambda,
      outputPath: '$.Payload',
    });

    // Map State to process batches
    const batchProcessingTask = new sfn.Map(this, 'Process Batches', {
      itemsPath: '$.inputBatchesS3Keys',
      maxConcurrency: 10,
      resultPath: '$.output.results',
      outputPath: '$.output',
    });

    // Lambda invocation task inside the Map state
    const processBatchTask = new tasks.LambdaInvoke(this, 'Get EPD data', {
      lambdaFunction: getEpdDataLambda,
      outputPath: '$.Payload',
    });

    batchProcessingTask.itemProcessor(processBatchTask);


    // Step Function definition
    const definition = getAllEpdInfosTask.next(batchProcessingTask);

    const stateMachine = new sfn.StateMachine(this, 'ExtractEpdRawDataEcoPlatformSfn', {
      definitionBody: sfn.DefinitionBody.fromChainable(definition),
      timeout: cdk.Duration.minutes(60),
    });
  }
}
