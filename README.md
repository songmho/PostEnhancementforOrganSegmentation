# LiverCancerAnalyzer
## Purpose 
 The project is to implement liver cancer diagnosis in console and web-based system  
 

## Requirement
### Programs  
 - Python: 3.7.6  
 - CUDA 11.2  
 - CUDNN 8.1  
 - MySQL  
### Python Libraries
 - TensorFlow: 2.5  
 - openCV: 4.5.1.58  
 - numpy: 1.19.5  
 - scikit-learn: 0.22.1   
 - keras: 2.6.0 
 - pandas: 1.0.1  
 - scikit-image: 0.16.2  
 - django: 3.1.1  
 - python-gdcm
 - pydicom: 2.0.0  
 - nibabel: 3.2.1
 - scipy: 1.4.1


## Configuration
Based on Django Project Structure  
**Project**  
  ├ **Test/examples**  
  ├ **miaas**: Folder for Containing  
  ├ **miaas_server**: Folder for Project Settings   
  ├ **refer/bootstrap-3.3.6**    
  ├ **static** : Folder for Static Files (JS, CSS, Libraries based JS)   
  ├ **templates/miaas** : Folder for html files  
  ├ **db.sqlite3** : Database for Project  
  └ **manage.py**: Python File for Managing Django Project   
  
  
## Implementation
### Implementation as Web based System  
#### Defining Tables in Django Default   
Enter the following commend in the console.  
The file location of the console is the root location of the project.  
```
python manage.py makemigrations
python.manage.py migrate
```
#### Importing Tables in MySQL 
...  
#### Running Django Project
Enter the following commend in the console.  
The file location of the console is the root location of the project.  
```
python manage.py runserver 0.0.0.0:8000
```

### Implementation as Console Based System  
To use the file in the location; miaas/lirads/software_process/main_process_v2.py  
https://github.com/Medical-Liver-Cancer-with-LI-RADS/LiverCancerAnalyzer/blob/master/miaas/lirads/software_process/main_process_v2.py   
1. Set path of medical images based on DICOM Format
    The medical images consist of the Following structure;  
    **Medical Image**  
    ├ MRN  
    &nbsp;&nbsp;├ MRN+"_"+ACQUIRED_DATE  
    &nbsp;&nbsp;&nbsp;&nbsp;├ PHASE 1  
    &nbsp;&nbsp;&nbsp;&nbsp;├ PHASE 2  
    &nbsp;&nbsp;&nbsp;&nbsp;├ ...  
            
2. Run code 
