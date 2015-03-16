#Manage Versions
import arcpy
import pprint
import os
from arcpy import env  
import yaml


#create version
def createver(key,workspace):
  #loop keys for versions
  #get version name and attemp to create new version
  for k in key:
   for key in k: 
     if 'version-name' in key:
       
       #Execute CreateVersion
       #attemp to create new version
       try:
          arcpy.CreateVersion_management(workspace, k['parent-version'], k['version-name'], k['access-permission']) 
        except:
          print 'Failed'
       
       #Alter Version
       #attemp to alter version
       try:
         arcpy.AlterVersion_management(workspace,  k['version-name'],  k['version-name'], 'version for: '+ k['version-name'], k['access-permission'])
       except:
         print 'Failed'

#delete version
def deletever(key,workspace):
  #loop keys for versions
  #get version name and attemp to delete version
  for k in key:
   for key in k:
     if 'version-name' in key:
      try:
         arcpy.DeleteVersion_management(workspace, k['version-name'],) 
       except:
         print 'Failed'

#delete sde connections 
def deleteconn(configkey):
  #delte existing sde file if it exsists
  if configkey['out_folder_path'] is None:
    os.path.exists(configkey['out_name']) and os.remove(configkey['out_name'])
  else:
    os.path.exists(configkey['out_folder_path']+configkey['out_name']) and os.remove(configkey['out_folder_path']+configkey['out_name'])

#create sde connections from config.yaml
def connsde( configkey ):
  #delete connection
  deleteconn(configkey)
  #arcpy create connection  
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
  #loop keys and create sde connection
  for k in connections:
    connsde(k)

  #delete
  for k in connections:
    #loop version keys and delete versions if the exist
    if  'versions' in k:
      if k['out_folder_path'] is not None:
        deletever(ver,k['out_folder_path']+k['out_name'])
      else:
        deletever(ver,k['out_name'])
 
  #compress
  for k in connections:
       #loop version keys and compress sde this compress state tree
      if k['out_folder_path'] is not None:
        arcpy.Compress_management(k['out_folder_path']+k['out_name'])
      else:
        arcpy.Compress_management(k['out_name'])
  
  #create
  for k in connections:
     #loop version keys and re-create versions
    if  'versions' in k:
      if k['out_folder_path'] is not None:
        createver(ver,k['out_folder_path']+k['out_name'])
      else:
        createver(ver,k['out_name']) 
