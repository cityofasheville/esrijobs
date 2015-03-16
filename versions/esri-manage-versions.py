#Manage Versions
import arcpy
import pprint
import os
from arcpy import env  
import yaml

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
    if k['out_folder_path'] is not None:
      versions = arcpy.ListVersions(k['out_folder_path']+k['out_name'])
    else:
      versions = arcpy.ListVersions(k['out_name'])
    print(versions)

