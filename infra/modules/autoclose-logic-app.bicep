@description('Azure region')
param location string

@description('Azure DevOps organization name')
param adoOrganization string

@description('Azure DevOps project name')
param adoProject string

@secure()
@description('Azure DevOps PAT with "Work Items: Read & Write" scope')
param adoPat string

var logicAppName = 'ghazdo-autoclose-${uniqueString(resourceGroup().id)}'
var workflowDefinition = loadJsonContent('../workflows/ghazdo-autoclose-only.json')

resource logicApp 'Microsoft.Logic/workflows@2019-05-01' = {
  name: logicAppName
  location: location
  tags: {
    purpose: 'GHAzDO-AutoClose'
    managedBy: 'Bicep'
  }
  properties: {
    state: 'Enabled'
    definition: workflowDefinition
    parameters: {
      adoOrganization: {
        value: adoOrganization
      }
      adoProject: {
        value: adoProject
      }
      adoPat: {
        value: adoPat
      }
    }
  }
}

output triggerUrl string = listCallbackUrl('${logicApp.id}/triggers/When_a_GHAzDO_alert_is_received', '2019-05-01').value
output logicAppName string = logicApp.name
output logicAppResourceId string = logicApp.id
