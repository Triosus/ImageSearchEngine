import cv2
import numpy as np
import math

#The number of bins for each of these determine the fitting of picture pixel information. Higher number of bins overfits while lower underfits.
H_DIVISIONS = 8
S_DIVISIONS = 12
V_DIVISIONS = 3

class ImageContainer:
    bin_main = [[0 for i in range(H_DIVISIONS * S_DIVISIONS * V_DIVISIONS )]for j in range(5)]
    height_main = 0
    width_main = 0

    def __init__ (self, path, main = False, sorting = 'Custom'):
        self.main = main
        self.path = path
        self.sorting = sorting
        image = cv2.imread(self.path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        self.image = image
        print(path)
        self.height, self.width, channel = image.shape
        
        #Uncomment this portion if image rescaling is required to fit orginal image size
        if(self.main == True):
            ImageContainer.height_main, ImageContainer.width_main, _ = image.shape
            self.width = ImageContainer.width_main 
            self.height = ImageContainer.height_main
        elif(self.height > ImageContainer.height_main or self.width > ImageContainer.width_main):
                image = cv2.resize(image, (ImageContainer.width_main, ImageContainer.height_main))
                self.width = ImageContainer.width_main
                self.height = ImageContainer.height_main

        #Following portion divides the image into five parts
        if(self.sorting == 'Custom'):
            center = np.zeros((self.height, self.width, 3), np.uint8)
            topleft = np.zeros((self.height, self.width, 3), np.uint8)
            topright = np.zeros((self.height, self.width, 3), np.uint8)
            bottomleft = np.zeros((self.height, self.width, 3), np.uint8)
            bottomright = np.zeros((self.height, self.width, 3), np.uint8)
        elif(self.sorting == 'OpenCV Histogram'):
            center = np.zeros((self.height, self.width, 1), np.uint8)
            topleft = np.zeros((self.height, self.width, 1), np.uint8)
            topright = np.zeros((self.height, self.width, 1), np.uint8)
            bottomleft = np.zeros((self.height, self.width, 1), np.uint8)
            bottomright = np.zeros((self.height, self.width, 1), np.uint8)

        center = cv2.ellipse(center, (self.width//2,self.height//2),(int(0.375*self.width),int(0.375*self.height)),0.0,0.0,360.0,(255,255,255),-1)
        
        topleft = cv2.rectangle(topleft, (0,0),(self.width//2,self.height//2),(255,255,255),-1)
        topleft = cv2.subtract(topleft, center)
        
        topright = cv2.rectangle(topright, (self.width,0),(self.width//2,self.height//2),(255,255,255),-1)
        topright = cv2.subtract(topright, center)
        
        bottomleft = cv2.rectangle(bottomleft, (0,self.height),(self.width//2,self.height//2),(255,255,255),-1)
        bottomleft = cv2.subtract(bottomleft, center)
        
        bottomright = cv2.rectangle(bottomright, (self.width,self.height),(self.width//2,self.height//2),(255,255,255),-1)
        bottomright = cv2.subtract(bottomright, center)

        if(self.sorting == "Custom"):
            center = cv2.bitwise_and(image, center, mask = None)
            topleft = cv2.bitwise_and(image, topleft, mask = None)
            topright = cv2.bitwise_and(image, topright, mask = None)
            bottomleft = cv2.bitwise_and(image, bottomleft, mask = None)
            bottomright = cv2.bitwise_and(image, bottomright, mask = None)
        
        #The RGB segregated images are converted to HSV format
        #center = cv2.cvtColor(center, cv2.COLOR_BGR2HSV)
        #topleft = cv2.cvtColor(topleft, cv2.COLOR_BGR2HSV)
        #topright = cv2.cvtColor(topright, cv2.COLOR_BGR2HSV)
        #bottomleft = cv2.cvtColor(bottomleft, cv2.COLOR_BGR2HSV)
        #bottomright = cv2.cvtColor(bottomright, cv2.COLOR_BGR2HSV)

        self.region = [topleft, topright, center, bottomleft, bottomright]

        self.BinSort()

    def BinSort(self):
        self.bin = [[0 for i in range(H_DIVISIONS * S_DIVISIONS * V_DIVISIONS)]for j in range(5)]
        if(self.sorting == 'Custom'):
            for i in range(5):
                totalpixels = 0
                for x in range(self.width):
                    for y in range(self.height):
                        h, s, v = self.region[i][y, x]
                        if (h != 0 and s != 0 and v != 0):
                            totalpixels += 1
                            v = math.ceil(v/(255/V_DIVISIONS)) -1
                            s = math.ceil(s/(255/S_DIVISIONS)) -1
                            h = math.ceil(h/(179/H_DIVISIONS)) -1
                            self.bin[i][S_DIVISIONS*V_DIVISIONS*h + s*V_DIVISIONS + v] += 1  #Places the pixel in a bin according to HSV value
                for n in range(H_DIVISIONS * S_DIVISIONS * V_DIVISIONS):
                #    self.bin[i][n] = round((self.bin[i][n]/totalpixels), 5)
                    self.bin[i][n] /= totalpixels
            if(self.main == True): ImageContainer.bin_main = self.bin
            #cv2.imshow("green", self.region[1]);cv2.waitKey();cv2.destroyAllWindows()

        elif(self.sorting == 'OpenCV Histogram'):
            for i in range(5):
                hist = cv2.calcHist([self.image],[0,1,2], self.region[i],[H_DIVISIONS,S_DIVISIONS,V_DIVISIONS],[0,180,0,256,0,256])
                hist = cv2.normalize(hist,hist).flatten()
                print(hist)
                for k in range((H_DIVISIONS*S_DIVISIONS*V_DIVISIONS)-1):
                    self.bin[i][k+1] = hist[k+1]
                if(self.main == True):  ImageContainer.bin_main[i] = self.bin[i]

    def Comparator(self):
        if(self.main == False):
            average = 0
            for i in range(5):
                average += self.chiSquare(i)
                #print(self.chiSquare(i))
            average /= 5
            return average
            #if(average <= 1): print("Image match found")
            #else: print("Image match not found")
        
    def chiSquare(self,i):
        d = 0.5* np.sum([(a-b)**2 / (a+b+float(1e-10)) for (a,b) in zip(self.bin[i],ImageContainer.bin_main[i])])
        return d


