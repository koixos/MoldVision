import Processor

if __name__ == '__main__':
    for i in range (1,4):
        img_path = "./data/" + str(i) + ".png"
        Processor.execute(img_path)