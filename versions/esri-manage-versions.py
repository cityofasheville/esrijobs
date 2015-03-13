import arcpy
import pprint
import os
from arcpy import env  
import yaml

def connsde( configkey ):

  if configkey['out_folder_path'] is not None:
    versions = arcpy.ListVersions(configkey['out_name'])
  else:
    versions = arcpy.ListVersions(os.path.join(configkey['out_folder_path'],configkey['out_name']))
  print(versions)

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

  if configkey['out_folder_path'] is not None:
    versions = arcpy.ListVersions(configkey['out_name'])
  else:
    versions = arcpy.ListVersions(os.path.join(configkey['out_folder_path'],configkey['out_name']))
  print(versions)


with open("config.yaml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

print cfg

for section in cfg:
    print(section)

print "\n"

for key, value in cfg.items():
  connections =  cfg[key]
  for k in connections:
    print k['out_folder_path']
    print "\n"
    connsde(k) 


