@description('Azure region')
param location string

@description('Azure DevOps organization name')
param adoOrganization string

@description('Azure DevOps project name')
param adoProject string

@secure()
@description('Azure DevOps PAT with Work Items (Read/Write) scope')
param adoPat string

@description('ADO work item type for secret alerts (defaults to Bug)')
param workItemType string = 'Bug'

var logicAppName = 'secret-scan-ado-${uniqueString(resourceGroup().id)}'
var workflowDefinition = loadJsonContent('../workflows/secret-scan-to-ado.json')

resource logicApp 'Microsoft.Logic/workflows@2019-05-01' = {
  name: logicAppName
  location: location
  tags: {
    purpose: 'GHAzDO-SecretScan-ADO'
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
      workItemType: {
        value: workItemType
      }
    }
  }
}

output triggerUrl string = listCallbackUrl('${logicApp.id}/triggers/When_a_Secret_Alert_Is_Received', '2019-05-01').value
output logicAppName string = logicApp.name
output logicAppResourceId string = logicApp.id
