from parse_data import vw_data
import os

if __name__ == '__main__':
    for i in range(10):
        # Create Training and Testing data
        train_folds = range(10)
        test_fold = [train_folds.pop(i)]
        fp = open('vw.train.data', 'w')
        fp.write(vw_data(train_folds).encode('utf-8'))
        fp.close()
        fp = open('vw.test.data', 'w')
        fp.write(vw_data(test_fold).encode('utf-8'))
        fp.close()

        #Run VW trough commandline
        os.system('vw --binary --passes 20 -c -k -f vw.model vw.train.data')
        os.system('vw --binary -t -i vw.model -r output.%d vw.test.data'%(i))
