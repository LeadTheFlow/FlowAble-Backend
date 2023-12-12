import subprocess

if __name__ == '__main__':
    #for the test
    subprocess.Popen(['python', 'apiTest.py']) #5000
    
    #Color detection
    subprocess.Popen(['python', 'color.py']) #5001
    
    #Product detection
    subprocess.Popen(['python', 'ocr_1.py']) #5002

    #for the test
    subprocess.Popen(['python', 'fileUpload.py']) #5003

    #Trashcan Detection
    subprocess.Popen(['python', 'detectTrash.py']) #5004
    
    