""" Image Utils
Copyright, 2018(c), Andrew Ferlitsch
Autor: David Molina @virtualdvid
"""

import os
import random
import shutil

class ImgUtils(object):
    """
    Image Utils: The img_utils module alows users to manage images datasets
                 (folders and images files) directly on disk.

    Type of Folder Tree

    ## tree = 1 ##
    [root_path] "folder_name"/..
        [subfolder] class_0/..
        [subfolder] class_1/..
        [subfolder] errors/..

    ## tree = 2 ##
    [root_path] "folder_name"/..
        [subfolder] train_tr/..
            [subfolder] class_0/..
            [subfolder] class_1/..
        [subfolder] train_val/..
            [subfolder] class_0/..
            [subfolder] class_1/..
        [subfolder] test/test/..
        [subfolder] errors/..
    """

    def __init__(self, root_path='./', tree=1, remove_folder=False):
        """
        Class Constructor
            :param root_path:      main image folder root
            :param tree:           type of folder tree
            :param remove_folder:  remove folder from directory
        """
        self.labels        = None           # list of images labels
        self.root_path     = None           # root folder where labels are located
        self.tree          = tree           # folder structure to the end sample
        self.remove_folder = remove_folder  # warning! remove folder from directory
        self._transf       = '1to2'         # type of folder tree to tranform '1to2' or '2to1'
        self._labels_org   = []             # list of origen paths
        self._end          = None           # add or remove name folder extentions (e.g. '_spl', ...)
        self._end2         = None           # add or remove name folder extentions (e.g. '_spl', ...)

        if not os.path.isdir(root_path):
            raise TypeError('String expected for directory path')
        else:
            self.labels = os.listdir(root_path)
            self.root_path = root_path

        if remove_folder:
            answere_ok = False
            while answere_ok is False:
                try:
                    warning = input('Warning! this will delete your image dataset. Are you sure? [Yes/no]: ')
                    warning = warning[0].lower()
                    if warning in ('y', 'n'):
                        answere_ok = True
                except:
                    continue
            if warning == 'y':
                shutil.rmtree(self.root_path)
                print('Your files were deleted')

    def _tree2_path(self):
        """ Getting path for 2to1 """
        if self._transf == '2to1':
            self.root_path = self.root_path.split('/')
            self.root_path = '/'.join(self.root_path[:-1])

    def _list_labels_org(self):
        """ List Labels Origin """
        # list of labels into root_path folder
        if self._transf == '1to2':
            self._labels_org = ['{}/{}'.format(self.root_path, lb) for lb in self.labels]
        elif self._transf == '2to1':
            train_tr = ['{}/train_tr/{}'.format(self.root_path, lb) for lb in self.labels]
            train_val = ['{}/train_val/{}'.format(self.root_path, lb) for lb in self.labels]
            self._labels_org = train_tr + train_val

    def _makedirs(self):
        """ Make Directories """
        #creates folders structure
        if self.tree == 1:
            if self._transf == '2to1':
                self.root_path = self.root_path[:-3]
            for lb in self.labels:
                os.makedirs('{}{}/{}'.format(self.root_path, self._end, lb), exist_ok=True)
        elif self.tree == 2:
            for lb in self.labels:
                os.makedirs('{}{}/train_tr/{}'.format(self.root_path, self._end2, lb), exist_ok=True)
                os.makedirs('{}{}/train_val/{}'.format(self.root_path, self._end2, lb), exist_ok=True)
            os.makedirs('{}{}/test/test'.format(self.root_path, self._end2), exist_ok=True)
            os.makedirs('{}{}/errors'.format(self.root_path, self._end2), exist_ok=True)
        elif self.tree is None:
            pass
        else:
            print('select between tree=1 or tree=2')

    def _copy_move(self, ppath, action, lb, img_list, index):
        """
        Copy or Move images
        :param ppath:     Required. Partial path
        :param action:    Required. Select between 'copy' or 'move'
        :param lb:        Required. Label name
        :param img_list:  Required. List of images per class
        :param index:     Required. Index image in the list
        """
        # verify type of tree to transform
        label = lb.split('/')[-1]
        if self._transf == '1to2':
            org_file = '{}/{}'.format(lb, img_list[index])
            dst_file = '{}{}/{}/{}'.format(self.root_path, ppath, label, img_list[index])
        elif self._transf == '2to1':
            org_file = '{}/{}'.format(lb, img_list)
            dst_file = '{}/{}/{}'.format(self.root_path, label, img_list)

        # move or copy images into new tree structure
        if action == 'copy':
            shutil.copy(org_file, dst_file)
        elif action == 'move':
            shutil.move(org_file, dst_file)
        else:
            print('select copy or move')

    def img_container(self, action='copy', spl=5, shufle=False, img_split=0.2):
        """
        Images Container
        :param action:    Select between 'copy' or 'move'
        :param spl:       Select the number of pictures for label to create the sample
        :param shufle:    select ramdom images per label or the first images on the list
        :param img_split: percentage of split between train / val
        """
        # specifies the name for the root_path
        if action == 'copy':
            self._end  = '_spl'
            self._end2 = '_t2' + self._end
        elif action == 'move':
            self._end  = ''
            self._end2 = '_t2'
        else:
            print('select copy or move')

        # creates list of labels from root_path
        self._list_labels_org()

        # creates the directories
        self._makedirs()

        for lb in self._labels_org:
            # list of images per label
            img_list = os.listdir(lb)
            # total of images per class
            len_img_list = len(img_list)

            # sets a sample number or total of images per class to move or copy
            if action == 'copy':
                spl = spl
            elif action == 'move':
                spl = len_img_list
            else:
                print('select copy or move')

            if shufle:
                #get a random image sample
                list_index = random.sample(range(len_img_list), spl)
            else:
                #get the first images on folder
                list_index = list(range(spl))

            # move images from tree 2 to tree 1
            if self._transf == '2to1':
                for img in img_list:
                    ppath = None
                    action = 'move'
                    index = None
                    self._copy_move(ppath, action, lb, img, index)
                self.tree = None

            # copy or move selected images into the sample labels depending of the selected tree
            if self.tree == 1:
                for index in list_index:
                    self._copy_move('_spl', action, lb, img_list, index)

            elif self.tree == 2:
                img_tr = int(len(list_index) * (1 - img_split))
                count = 0
                for index in list_index:
                    if count <= img_tr:
                        # move or copy images in the train folder
                        self._copy_move('{}/train_tr'.format(self._end2), action, lb, img_list, index)
                    else:
                        # move or copy images in the validation folder
                        self._copy_move('{}/train_val'.format(self._end2), action, lb, img_list, index)
                    count += 1
            elif self.tree is None:
                pass
            else:
                print('select 1 or 2')

    def transform(self, shufle=False, img_split=0.2):
        """
        Transform
        :param shufle:    select ramdom images per label or the first images on the list
        :param img_split: percentage of split between train / val
        :param transf:    type of folder tree to tranform '1to2' or '2to1'
        """

        # getting path for 2to1
        self._tree2_path()

        # move the files between tree structures
        action = 'move'
        if self._transf == '1to2':
            self.tree = 2
            spl = None
            self.img_container(action, spl, shufle, img_split)
            shutil.rmtree(self.root_path)
        elif self._transf == '2to1':
            old_path = self.root_path
            self.img_container(action)
            shutil.rmtree(old_path)
        else:
            print('select 1to2 or 2to1')

    def img_rename(self, text=None):
        """
        Rename Images
        :param text: Give a text for your images name
        """
        # creates source list
        if self.tree == 2:
            self._transf = '2to1'

        # getting path for 2to1
        self._tree2_path()

        self._list_labels_org()

        for lb in self._labels_org:
            # list of images per label
            img_list = os.listdir(lb)
            # extract label name
            text_lb = lb.split('/')[-1]
            for i, img in enumerate(img_list):
                if os.path.isdir('{}/{}'.format(lb, img)):
                    print('There is not images to rename')
                    break
                dtype = img.split('.')[-1]
                if text is True:
                    img_name = '{}_{}'.format(text_lb, i)
                elif text is not None:
                    img_name = '{}_{}'.format(text, i)
                else:
                    img_name = i
                os.rename('{}/{}'.format(lb, img), '{}/{}.{}'.format(lb, img_name, dtype))

    def img_replace(self, old, new, img_id=False):
        """
        Rename Images
        :param old:    Required. The text you want to replace.
        :param new:    Required. The text you want to replace "old" with.
        :param img_id: True to enumerate by id name_id
        """
        # creates source list
        if self.tree == 2:
            self._transf = '2to1'

        # getting path for 2to1
        self._tree2_path()

        self._list_labels_org()

        for lb in self._labels_org:
            # list of images per label
            img_list = os.listdir(lb)
            for i, img in enumerate(img_list):
                if os.path.isdir('{}/{}'.format(lb, img)):
                    print('There is not images to replace')
                    break
                if img_id:
                    os.rename('{}/{}'.format(lb, img), '{}/{}'.format(lb, img.replace(old, '{}_{}'.format(new, i))))
                else:
                    os.rename('{}/{}'.format(lb, img), '{}/{}'.format(lb, img.replace(old, new)))

    @property
    def transf(self):
        """ Getter for image transform """
        return self._transf

    @transf.setter
    def transf(self, transf):
        """
        Setter for image transform
            :param transf: type of folder tree to tranform '1to2' or '2to1'
        """
        self._transf = transf

    @property
    def labels_org(self):
        """ Getter for list of origen paths """
        return self._labels_org

    @property
    def end(self):
        """ Getter for name folder extentions (e.g. '_spl', ...) """
        return self._end

    @property
    def end2(self):
        """ Getter for name folder extentions (e.g. '_spl', ...) """
        return self._end2
