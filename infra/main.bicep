targetScope = 'resourceGroup'

@description('Azure region for all resources')
param location string = resourceGroup().location

@description('Azure DevOps organization name (e.g. "myorg" from https://dev.azure.com/myorg)')
param adoOrganization string

@description('Azure DevOps project name')
param adoProject string

@secure()
@description('Azure DevOps PAT with "Work Items: Read & Write" scope')
param adoPat string

@secure()
@description('GitHub PAT with "security_events" scope')
param githubPat string

@secure()
@description('Shared secret for GitHub webhook HMAC-SHA256 validation')
param webhookSecret string

@description('ADO work item type to create (e.g. Issue, Bug, Task)')
param workItemType string = 'Issue'

module logicApp 'modules/logic-app.bicep' = {
  name: 'ghas-ado-logic-app'
  params: {
    location: location
    adoOrganization: adoOrganization
    adoProject: adoProject
    adoPat: adoPat
    githubPat: githubPat
    webhookSecret: webhookSecret
    workItemType: workItemType
  }
}

module secretScanLogicApp 'modules/secret-scan-logic-app.bicep' = {
  name: 'secret-scan-ado-logic-app'
  params: {
    location: location
    adoOrganization: adoOrganization
    adoProject: adoProject
    adoPat: adoPat
  }
}

output logicAppCallbackUrl string = logicApp.outputs.triggerUrl
output logicAppName string = logicApp.outputs.logicAppName
output logicAppResourceId string = logicApp.outputs.logicAppResourceId
module autocloseLogicApp 'modules/autoclose-logic-app.bicep' = {
  name: 'ghazdo-autoclose-logic-app'
  params: {
    location: location
    adoOrganization: adoOrganization
    adoProject: adoProject
    adoPat: adoPat
  }
}

output secretScanCallbackUrl string = secretScanLogicApp.outputs.triggerUrl
output secretScanLogicAppName string = secretScanLogicApp.outputs.logicAppName
output secretScanLogicAppResourceId string = secretScanLogicApp.outputs.logicAppResourceId
output autocloseCallbackUrl string = autocloseLogicApp.outputs.triggerUrl
output autocloseLogicAppName string = autocloseLogicApp.outputs.logicAppName
output autocloseLogicAppResourceId string = autocloseLogicApp.outputs.logicAppResourceId
