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

module autocloseLogicApp 'modules/autoclose-logic-app.bicep' = {
  name: 'ghazdo-autoclose-logic-app'
  params: {
    location: location
    adoOrganization: adoOrganization
    adoProject: adoProject
    adoPat: adoPat
  }
}

output autocloseCallbackUrl string = autocloseLogicApp.outputs.triggerUrl
output autocloseLogicAppName string = autocloseLogicApp.outputs.logicAppName
