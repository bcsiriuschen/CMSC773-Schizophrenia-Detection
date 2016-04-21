import os
if __name__ == '__main__':

    # Input Parameters
    input_file = 'vw.output'
    groundtruth_file = 'groundtruth.output'
    output_file = 'vw.tpfp'

    #Compute 0/1 Accuracy
    result = [float(x) for x in open(input_file).readlines()]
    groundtruth = [float(x) for x in open(groundtruth_file).readlines()]
    total = len(result)
    correct = 0
    for (i, score) in enumerate(result):
        if float(score)*float(groundtruth[i]) > 0:
            correct += 1
    print '0/1 Accuracy: %.4f'%(float(correct)/total)

    #Generate TP-FP pairs for ROC curve and AUC
    total_positive = sum([1 for x in groundtruth if x > 0])
    total_negative = sum([1 for x in groundtruth if x < 0])
    curr_pos_count = 0
    curr_neg_count = 0
    true_positive = []
    false_positive = []
    sorted_groundtruth = [groundtruth[i] for i in sorted(range(total), key=lambda i: result[i], reverse=True)]
    fp = open(output_file, 'w')
    for label in sorted_groundtruth:
        if label > 0:
            curr_pos_count += 1
        else:
            curr_neg_count += 1
            true_positive.append(float(curr_pos_count)/total_positive)
            false_positive.append(float(curr_neg_count)/total_negative)
    for i, tp in enumerate(true_positive):
        fp.write('%f %f\n'%(tp, false_positive[i]))
    
    #Compute AUC
    temp1 = [x-y for (x,y) in zip(false_positive[1:],false_positive[:-1])]
    temp2 = [x+y for (x,y) in zip(true_positive[1:], true_positive[:-1])]
    auc = 0.5*sum([x*y for (x,y) in zip(temp1, temp2)]);
    print 'AUC: %.4f'%(auc)

    #plot ROC curve using gnuplot
    os.system('gnuplot %s'%(output_file))