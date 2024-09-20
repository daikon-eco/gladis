#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { ConnectorsStack } from '../lib/connectors';
import { ACCOUNT_ID, REGION, Stage } from '../lib/constants'

const app = new cdk.App();
const stage = Stage.Prod;

new ConnectorsStack(app, `ConnectorsStack-${stage}-${REGION}`, {
  stage: stage,
  env: { account: ACCOUNT_ID, region: REGION },
});
