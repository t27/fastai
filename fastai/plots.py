from .imports import *
from .torch_imports import *
from sklearn.metrics import confusion_matrix

def ceildiv(a, b):
    return -(-a // b)

def plots(ims, figsize=(12,6), rows=1, interp=False, titles=None, maintitle=None):
    if type(ims[0]) is np.ndarray:
        ims = np.array(ims)
        if (ims.shape[-1] != 3): ims = ims.transpose((0,2,3,1))
    f = plt.figure(figsize=figsize)
    if maintitle is not None:
        plt.suptitle(maintitle, fontsize=16)
    for i in range(len(ims)):
        sp = f.add_subplot(rows, ceildiv(len(ims), rows), i+1)
        sp.axis('Off')
        if titles is not None: sp.set_title(titles[i], fontsize=16)
        plt.imshow(ims[i], interpolation=None if interp else 'none')


def plots_from_files(imspaths, figsize=(10,5), rows=1, titles=None, maintitle=None):
    """Plots images given image files.

    Arguments:
        im_paths (list): list of paths
        figsize (tuple): figure size
        rows (int): number of rows
        titles (list): list of titles
        maintitle (string): main title
    """
    f = plt.figure(figsize=figsize)
    if maintitle is not None: plt.suptitle(maintitle, fontsize=16)
    for i in range(len(imspaths)):
        sp = f.add_subplot(rows, ceildiv(len(imspaths), rows), i+1)
        sp.axis('Off')
        if titles is not None: sp.set_title(titles[i], fontsize=16)
        img = plt.imread(imspaths[i])
        plt.imshow(img)


def plot_confusion_matrix(cm, classes, normalize=False, title='Confusion matrix', cmap=plt.cm.Blues):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    (This function is copied from the scikit docs.)
    """
    plt.figure()
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    if normalize: cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
    print(cm)
    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, cm[i, j], horizontalalignment="center", color="white" if cm[i, j] > thresh else "black")

    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')

def plots_raw(ims, figsize=(12,6), rows=1, titles=None):
    f = plt.figure(figsize=figsize)
    for i in range(len(ims)):
        sp = f.add_subplot(rows, ceildiv(len(ims), rows), i+1)
        sp.axis('Off')
        if titles is not None: sp.set_title(titles[i], fontsize=16)
        plt.imshow(ims[i])

def load_img_id(ds, idx, path): return np.array(PIL.Image.open(path+ds.fnames[idx]))


class ImageModelResults():
    """
    Visualize the results of an image model

    Each function has an extra parameter, y, which is the selected_class in (0,num_classes-1)
    y is a number in the case of displaying the most correct/incorrect classes
    y is a vector in the case of displaying the most uncertain classes
    """

    def __init__(self, ds, log_preds):
        self.ds = ds
        self.preds = np.argmax(log_preds, axis=1)
        self.probs = np.exp(log_preds)

    def plot_val_with_title(self, idxs, y):
        imgs = np.stack([self.ds[x][0] for x in idxs])
        if isinstance(y, int):
            title_probs = [self.probs[x,y] for x in idxs]
        else:
            title_probs = [self.probs[x,y[i]] for i,x in enumerate(idxs)]

        return plots(self.ds.denorm(imgs), rows=1, titles=title_probs)

    def most_by_mask(self, mask, y, mult):
        idxs = np.where(mask)[0]
        return idxs[np.argsort(mult * self.probs[idxs,y])[:4]]

    def most_by_correct(self, y, is_correct):
        """
        mult=-1 when the is_correct flag is true -> when we want to display
        the most correct classes we will make a descending sorting (argsort)
        because we want that the biggest probabilities to be displayed first.
        When is_correct is false, we want to display the most incorrect classes,
        so we want an ascending sorting since our interest is in the smallest probabilities.
        """
        mult = -1 if is_correct==True else 1
        return self.most_by_mask(((self.preds == self.ds.y)==is_correct)
                                 & (self.ds.y == y), y, mult)

    def plot_by_correct(self, y, is_correct):
        return self.plot_val_with_title(self.most_by_correct(y, is_correct), y)


    def plot_most_correct(self, y): return self.plot_by_correct(y, True)
    def plot_most_incorrect(self, y): return self.plot_by_correct(y, False)

