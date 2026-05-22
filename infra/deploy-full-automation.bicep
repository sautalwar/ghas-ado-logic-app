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

@description('ADO work item type to create (e.g. Issue, Bug, Task)')
param workItemType string = 'Issue'

@description('State to set when closing work items. Agile="Closed", Scrum="Done", Basic="Done", CMMI="Closed"')
param closedState string = 'Done'

module ghazdoLogicApp 'modules/ghazdo-logic-app.bicep' = {
  name: 'ghazdo-full-automation-logic-app'
  params: {
    location: location
    adoOrganization: adoOrganization
    adoProject: adoProject
    adoPat: adoPat
    workItemType: workItemType
    closedState: closedState
  }
}

output triggerUrl string = ghazdoLogicApp.outputs.triggerUrl
output logicAppName string = ghazdoLogicApp.outputs.logicAppName
