#Manage Versions
import arcpy
import pprint
import os
from arcpy import env  
import yaml


#create version
def createver(key,workspace):
  for k in key:
   for key in k: 
     if 'version-name' in key:
       
       #Execute CreateVersion
       arcpy.CreateVersion_management(workspace, k['parent-version'], k['version-name'], k['access-permission']) 
       
       #Alter Version
       arcpy.AlterVersion_management(workspace,  k['version-name'],  k['version-name'], 'version for: '+ k['version-name'], k['access-permission'])

#delete version
def deletever(key,workspace):
  for k in key:
   for key in k:
     if 'version-name' in key:
       arcpy.DeleteVersion_management(workspace, k['version-name'],) 

#delete sde connections 
def deleteconn(configkey):
  if configkey['out_folder_path'] is None:
    os.path.exists(configkey['out_name']) and os.remove(configkey['out_name'])
  else:
    os.path.exists(configkey['out_folder_path']+configkey['out_name']) and os.remove(configkey['out_folder_path']+configkey['out_name'])

#create sde connections from config.yaml
def connsde( configkey ):
  deleteconn(configkey)  
  arcpy.CreateDatabaseConnection_management(configkey['out_folder_path'],
                                            configkey['out_name'],
                                            configkey['database_platform'],
                                            configkey['instance'],
                                            configkey['account_authentication'],
                                            configkey['username'],
                                            configkey['password'],
                                            configkey['save_user_pass'],
                                            configkey['database'],
                                            configkey['schema'],
                                            configkey['version_type'],
                                            configkey['version'],
                                            configkey['date'])
#get yaml configuration file
with open("config/config.yaml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

#traverse yaml create sde conenction string to remove,create, and alter versions
for key, value in cfg.items():
  connections =  cfg[key]
  for k in connections:
    connsde(k)

  #delete
  for k in connections:
    if  'versions' in k:
      ver = k['versions']
      if k['out_folder_path'] is not None:
        deletever(ver,k['out_folder_path']+k['out_name'])
      else:
        deletever(ver,k['out_name'])
 
  #compress
  for k in connections:
      if k['out_folder_path'] is not None:
        arcpy.Compress_management(k['out_folder_path']+k['out_name'])
      else:
        arcpy.Compress_management(k['out_name'])
  
  #create
  for k in connections:
    if  'versions' in k:
      ver = k['versions']
      if k['out_folder_path'] is not None:
        createver(ver,k['out_folder_path']+k['out_name'])
      else:
        createver(ver,k['out_name']) 
