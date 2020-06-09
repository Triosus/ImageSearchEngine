from icrawler.builtin import BingImageCrawler
from ImageContainer import *
import pathlib
import os
import sys

class ImageFinder:
    def __init__(self, sourcePath, keyword, num):
        self.sourcePath = sourcePath
        self.keyword = keyword
        bingcrawler = BingImageCrawler(storage={'root_dir':'Image Database\\'+self.keyword+'\\'})
        bingcrawler.crawl(keyword=self.keyword,max_num = num)
        self.Sorter()

    def Sorter(self):
        ImageContainer(self.sourcePath, main = True)
        SimilarityIndex = []
        OrignalFileNumber = []
        count = 0
        for path in pathlib.Path('Image Database\\'+self.keyword+'\\').iterdir():
            tempImageContainer = ImageContainer(str(path))
            SimilarityIndex.append(tempImageContainer.Comparator())
            OrignalFileNumber.append(count+1)
            count += 1
        SimilarityIndex.append(-1)
        OrignalFileNumber.append(-1)
        k = 0
        for n in range(count):
            for i in range(count-k):
                if(SimilarityIndex[i] > SimilarityIndex[i+1]):
                    SimilarityIndex[-1] = SimilarityIndex[i]
                    SimilarityIndex[i] = SimilarityIndex[i+1]
                    SimilarityIndex[i+1] = SimilarityIndex[-1]
                    OrignalFileNumber[-1] = OrignalFileNumber[i]
                    OrignalFileNumber[i] = OrignalFileNumber[i+1]
                    OrignalFileNumber[i+1] = OrignalFileNumber[-1]
            k += 1

        for x in range(k):
            if(OrignalFileNumber[x]/10 < 1):
                os.rename('Image Database\\'+self.keyword+'\\00000'+str(OrignalFileNumber[x])+'.jpg','Image Database\\'+self.keyword+'\\Sorted_00000'+str(x+1)+'.jpg')
            elif(OrignalFileNumber[x]/100 < 1):
                os.rename('Image Database\\'+self.keyword+'\\0000'+str(OrignalFileNumber[x])+'.jpg','Image Database\\'+self.keyword+'\\Sorted_00000'+str(x+1)+'.jpg')
            elif(OrignalFileNumber[x]/1000 < 1):
                os.rename('Image Database\\'+self.keyword+'\\000'+str(OrignalFileNumber[x])+'.jpg','Image Database\\'+self.keyword+'\\Sorted_00000'+str(x+1)+'.jpg')
            elif(OrignalFileNumber[x]/10000 < 1):
                os.rename('Image Database\\'+self.keyword+'\\00'+str(OrignalFileNumber[x])+'.jpg','Image Database\\'+self.keyword+'\\Sorted_00000'+str(x+1)+'.jpg')
            elif(OrignalFileNumber[x]/100000 < 1):
                os.rename('Image Database\\'+self.keyword+'\\0'+str(OrignalFileNumber[x])+'.jpg','Image Database\\'+self.keyword+'\\Sorted_00000'+str(x+1)+'.jpg')

        f = open("Image Database\\"+self.keyword+"\\Similarity Indices.txt", "w")
        for i in range(count):
            f.write("File Number: {:>5}    |     Similarity Index: {:<18}     |\n".format(str(i+1),str(SimilarityIndex[i])))