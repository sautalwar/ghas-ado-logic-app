@description('Azure region')
param location string

@description('Azure DevOps organization name')
param adoOrganization string

@description('Azure DevOps project name')
param adoProject string

@secure()
@description('Azure DevOps PAT')
param adoPat string

@secure()
@description('GitHub PAT (optional; not required for the webhook-driven secrets-only flow)')
param githubPat string = ''

@secure()
@description('Webhook secret shared with the GitHub webhook (optional)')
param webhookSecret string = ''

@description('ADO work item type')
param workItemType string = 'Issue'

@description('State to set when closing work items. Agile="Closed", Scrum="Done", Basic="Done", CMMI="Closed"')
param closedState string = 'Done'

var logicAppName = 'ghas-ado-sync-${uniqueString(resourceGroup().id)}'
var workflowDefinition = loadJsonContent('../workflows/ghas-to-ado.json')

resource logicApp 'Microsoft.Logic/workflows@2019-05-01' = {
  name: logicAppName
  location: location
  tags: {
    purpose: 'GHAS-ADO-Sync'
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
      githubPat: {
        value: githubPat
      }
      webhookSecret: {
        value: webhookSecret
      }
      workItemType: {
        value: workItemType
      }
      closedState: {
        value: closedState
      }
    }
  }
}

output triggerUrl string = listCallbackUrl('${logicApp.id}/triggers/When_a_GHAS_webhook_is_received', '2019-05-01').value
output logicAppName string = logicApp.name
output logicAppResourceId string = logicApp.id
