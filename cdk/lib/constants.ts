import { Runtime } from 'aws-cdk-lib/aws-lambda';

export enum Stage {
  Beta = 'beta',
  Gamma = 'gamma',
  Prod = 'prod',
}

export const REGION = 'eu-west-3';
export const ACCOUNT_ID = '376129870118';
export const LAMBDA_PYTHON_RUNTIME = Runtime.PYTHON_3_9;
