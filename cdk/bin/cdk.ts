#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { EtlStack } from '../lib/etl';
import { ACCOUNT_ID, REGION, Stage } from '../lib/constants'

const app = new cdk.App();
const stage = Stage.Prod;

new EtlStack(app, `DatabaseStack-${stage}-${REGION}`, {
  stage: stage,
  env: { account: ACCOUNT_ID, region: REGION },
});
