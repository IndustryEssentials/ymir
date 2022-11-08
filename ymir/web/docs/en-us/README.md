# Introduction

Hi, welcome to the YMIR model production platform, which promote algorithm technology progress by provides end-to-end algorithm development tools for algorithm developers and one-stop services around data processing, model training and other requirements required in the AI development process. Currently, YMIR system supports target detection class model training, which is mainly used to detect the position and category of each object in the diagram. It is suitable for scenarios where there are multiple subjects in the diagram to be identified, or the location and number of subjects to be identified.


# Specialized Nouns

- Class: Class generally refers to the keywords added by users to the YMIR system. These keywords are usually used for training, labeling, i.e., the target objects that users want to detect in the diagram.
    
- Class Alias: Alias generally corresponds to the main name of a class. When a user adds an alias to a class, the annotation box corresponding to the alias will be classified by the main name of the class during training.
    
- Asset Tag: The tag of a single image data, usually refers to a certain attribute of the image, such as the location of the image's origin, the scene it belongs to, etc.
    
- Box Tag: The tag classification of a single annotation box, generally refers to a certain attribute of the annotation box, such as the quality, resolution, etc.
    
- Target: The training target is selected by the user in the class, i.e. the object that the current model to be trained wants to detect.
    
- DockerImage: The environment for running training, mining and inference tasks. YMIR system provides some default dockerimages, and also supports users to develop and upload their own.
    
- GroundTruth(GT): The correct annotation value in the dataset, which is used as the reference annotation of the target to be identified, usually annotated manually.
    
- Prediction: The annotation result generated from the dataset after model inference, which is used to evaluate the recognition effect of the model.
    
- Iteration: YMIR provides a standardized model iteration process and helps the user fill in the previous operation result by default in each step of the operation. The main goal of iteration is to help users get better quality training data and better models.
   
- Deployment: Model as a Service. Model deployment refers to packaging the model inference details into the model and realizing the inference work of all deep learning models through a set of APIs. A standard http interface is provided to support fast user integration and validation.

# Usage Process

The usage flow of YMIR system is generally divided into two categories, one is the meta-operation of the system, including data management, processing, analysis, labeling, and model training, diagnosis, deployment and other functions, the whole process is visualized and easy to operate. Other one is the iterative process provided by the system, which breaks down the key steps in model training and helps users fill in the data to support them in optimizing the model and obtaining the final training results. To learn more about iteration-related operations, please jump to [Model iteration](en-us/README.md#model-iteration).

We will talk about each step in detail next, and if you have any other questions, please email us at contact.viesc@gmail.com.

## Create Projects

First of all, we need to create project in [project management], YMIR system uses project as the dimension for data and model management.

![create_a_project_1](https://user-images.githubusercontent.com/90443348/197174653-99973fcf-9368-4741-8b68-447f246a6c18.png)

![create_a_project_2](https://user-images.githubusercontent.com/90443348/197174826-f6eef2bf-a016-4d37-84cb-0336b707a058.png)

Please note that the training target of the project will be set by default to the training goal you had when [Iterative Process] was enabled.

## Adding Datasets

After the project is created, you need to add datasets to the project, import and label the data before training.

### Adding Classes

Determine which objects you want to identify before uploading. Each category corresponds to one of the objects you want to detect in the image, and add the corresponding class to [Class Management].

### Prepare Dataset

Prepare the dataset based on the added classes, with the following format requirements.

- Only zip format zip files are supported for upload.
    
- Recommended <200MB for zip file size uploads within the Internet and <1G within the LAN, and path import for datasets over 1G.
    
- Supports image types of png, jpg, bmp, jpeg, images that do not match the format will not be imported.
    
- If the annotation files need to be imported simultaneously, the annotation file format needs to be Pascal VOC.
    
- The image files should be placed in the images folder, the groundtruth files should be placed in the gt folder, and the prediction annotation files should be placed in the pred folder, and the pred folder should contain the model information that generated the prediction results. gt and pred are optional, if not uploaded, the folder should be empty, and the file structure in the zip package is as follows. Click to download the example file: [Sample.zip](https://github.com/IndustryEssentials/ymir-images/blob/main/doc_v2/sample_dataset.zip?raw=true)

![sample_zip](https://user-images.githubusercontent.com/90443348/197174963-a5d818aa-5d26-4742-99c8-3b23f693be1d.png)

### Uploading the Dataset

After you have finished adding categories and preparing data, click the [Add dataset] button to enter the Add dataset page.

![create_a_dataset_1](https://user-images.githubusercontent.com/90443348/197175120-b7dbe772-83fd-4802-97fc-4d03f2f9e87c.png)

Data can be imported by the following ways.

① User's local data: Support local uploading of compressed packages, or importing via network url or path, and the path import requires putting the dataset file under `ymir-workplace/ymir-sharing`, and then filling in the path address `ymir-workplace/ymir-sharing/voc2012` on the import page. 

![create_a_dataset_2](https://user-images.githubusercontent.com/90443348/197175212-392997ae-e25e-4dd3-a4b6-041ea9464a5e.png)

② Existing data of the platform: Support copying other datasets under this user or importing existing public datasets of the platform.

![create_a_dataset_3](https://user-images.githubusercontent.com/90443348/197175249-9c655cfa-4db3-4a1a-aa16-ddc3d84876bb.png)

## Data Mining

YMIR provides users with sophisticated mining algorithms. The main purpose of data mining is to find data that is useful for model training in unlabeled data. Generally the target data set for mining comes from field data or relevant scenarios, and high value quality data can be found in it after mining. By this way, the labeling cost can be reduced and training set can be expanded after the completion of labeling.

First select the dataset to be mined, click [Mine] operation, and create a mining task.

![mining_1](https://user-images.githubusercontent.com/90443348/197175639-84ce9a2e-404d-449f-b6ea-dd40295558c7.png)

![mining_2](https://user-images.githubusercontent.com/90443348/197183451-4027791b-3c4f-41b1-9642-e48b729c9749.png)

The topk value is the total amount of data mined, and the mining model should be the one that you expect to improve the effect, if there is a lack of model, you should go to [Model Training] or [Model Import] to get it.

## Data Annotation

If the uploaded dataset does not contain annotation files or you need to re-annotate it, you can enter the data annotation page to annotate it.

Step 1 First select the dataset to be annotated and click [Annotate] to create the annotation task.

![labelling_1](https://user-images.githubusercontent.com/90443348/197179707-f71f19cf-0d4a-4327-8fb2-1719b0c1b9a5.png)

Step 2 Fill in the content needed for annotation, the annotation target can be selected in the class list under the current user, support uploading annotation standard documents. If the user has not yet registered for the annotation platform account, click the link below to jump to the annotation platform to register an account.

![labelling_2](https://user-images.githubusercontent.com/90443348/197179797-3d8f1c03-77c1-450b-b8aa-81deb8576f63.png)

Step 3 After the annotation task is created, users can view the details of the annotated dataset and jump to the annotation platform to annotate it by themselves.

![labelling_3](https://user-images.githubusercontent.com/90443348/197180017-c067375d-6bad-44da-9e4d-3d232c5d817b.png)

## Data Analysis

You can access this function page by clicking [Dataset Analysis] from the left menu action bar under [Project Management].

Data analysis is designed to perform quality checks on the image data in your dataset, by providing objective metrics to guide you with reference to the next operations (annotation, training, diagnosis, etc.).

The overall quality check report will include statistics on metrics at both groundtruth value and prediction value.

The analysis results are divided into two categories: overall metrics and distribution metrics. The overall metrics include four categories: storage size, total number of labeled frames, average number of labeled frames, and the proportion of labeled images; the distribution metrics include six categories: image storage size distribution, image aspect ratio distribution, image resolution distribution, image quality distribution, labeled frame resolution distribution, and category proportion distribution.

The analysis report of different datasets can be viewed by switching the datasets, and multiple datasets can be selected for comparison.

![data_analysis_1](https://user-images.githubusercontent.com/90443348/197180186-9f112a9d-e6d7-4848-afc0-48f895c6b1dd.png)

## Model Training

### Function Page

You can access this function page by clicking [Model Training] from the left menu action bar under [Project Management].

![training_1](https://user-images.githubusercontent.com/90443348/197180300-3f6de7e0-db9c-4de4-9e76-26f97c1b9b5b.png)

If you have a specified dataset as the training set, you can also access the training page from the operation portal on the right side of the dataset.

![training_2](https://user-images.githubusercontent.com/90443348/197180387-11166212-8bac-4241-b931-1c3984a22130.png)

### Training configuration

![image](https://user-images.githubusercontent.com/90443348/197182072-320b792b-fb1c-42a1-9437-8f652749213b.png)

Step 1 Select a dockerimage

YMIR provides the default dockerimage, which supports yolo v5 training. If you need other images, you can go to [My images] - [Public images] list page by the administrator to pull more images, refer to [docker management](en-us/README.md#docker-management) for details.

Step 2 Select training set

Select the dataset you want to use for the model training. The optional list is the dataset under the current project, and cannot be selected across projects. Note that please make sure the selected dataset has been annotated, otherwise the training cannot be started, and the model may be better if the dataset is better annotated.

Step 3 Select the training target

The training target is the object category you want to recognize in this training, and it only supports the selection in the class list of the selected training set. After the selection is finished, you can click the [Calculate Positive and Negative Samples] button to calculate the percentage of the currently selected classes in the training set.

Step 4 Select the validation set

When the AI model is trained, each batch of training data will be tested for model effect, and the images in the validation set will be used as validation data to adjust the training through the result feedback. Therefore, it is necessary to select a data set that is consistent with the training target as the validation set for model improvement. The validation set also needs to be labeled data, otherwise it will affect the final model effect.

Step 5 Pre-training model

Pre-training model: In the model iteration training, the user adds training data to the original training data, and can train the model by loading the model parameters trained from the original training data. This can make the model converge faster and the training time shorter, and at the same time, the model results may be better if the dataset quality is higher.

Note: Only the model trained under the same training dockerimage can be selected as the pre-trained model.

Step 6 Number of GPUs

At present, YMIR only supports GPU training, so you can adjust the number of GPUs used for this training here to allocate resources reasonably.

Step 7 Hyperparameter Configuration

It is recommended that users who have some knowledge of deep learning should consider using it according to the actual situation. The hyper-parameter configuration provides the built-in parameter modification function of the dockerimage, and additionally provides the "longest edge scaling" configuration item.

- The longest length scaling: you can input the value to adjust the image size of the training data, set the longest edge of the image to the value you set, and scale the other edge length proportionally.

### Model Training

Click [Start Training] to train the model.

- The training time is related to the size of the data, 1000 images may take several hours to train, please be patient.

- During the training process, you can check the training progress of the model in the [Model List] page.

![training_4](https://user-images.githubusercontent.com/90443348/197182370-19df02ce-786f-444b-8a13-1f26606af568.png)

- To view more information about the model training process, you can open the [Model Details] page and click the [Training Process] button to view the training information.

![training_5](https://user-images.githubusercontent.com/90443348/197182427-4b2b514d-d692-4c9a-be36-8804c447f848.png)

![training_6](https://user-images.githubusercontent.com/90443348/197182469-a083e67b-7107-46ef-9a7b-cdef2facd31e.png)

## Model Diagnostics 

Model effects can be understood through model inference or model diagnostics.

### Model Inference

The [Inference] operation of the model generates inference results on the selected test set, and supports simultaneous selection of multiple data sets or models for inference.

![inference_1](https://user-images.githubusercontent.com/90443348/197182648-5a1c3562-7cb0-47f1-bfcc-2208fc491b65.png)

![inference_2](https://user-images.githubusercontent.com/90443348/197182868-641fef4b-345c-49b2-aed5-2235930cfc5c.png)

Support visualization of inference results after inference is completed.

![inference_3](https://user-images.githubusercontent.com/90443348/197183620-7122fe6a-1706-49fe-b82d-89b3f49b5803.png)

![inference_4](https://user-images.githubusercontent.com/90443348/197183664-7f937c92-ceec-42f9-939a-a4f707d3554c.png)

![inference_5](https://user-images.githubusercontent.com/90443348/197183705-1957172d-8cea-4294-a5aa-9c969ca76972.png)

The current visualization supports metrics evaluation of inference results, including FP, FN, TP and MTP, and supports filtering view by class.

FP: False Positive, the criteria value of the current test image does not contain the correct detection target, but the model identifies it incorrectly as the detection target. That is, a negative sample is predicted to be a positive class in the prediction result.

FN: False Negative, the criterion value of the current test image is the correct detection target, but the model does not recognize it or incorrectly identifies it as other targets. That is, the positive samples are predicted to be in the negative class in the prediction result.

TP: True Positive, i.e., the model prediction result that matches the standard value under the target prediction class.

MTP: Matched True Positive, i.e., the criterion that matches the prediction result under the target prediction class.

### Model Diagnosis

Find the [Model Diagnosis] module in the left navigation bar of [Project Management] to evaluate the effect of the model online. The specific operations are: ① select the model you want to evaluate, ② select the test set (the selected test set needs to have completed inference on the model, refer to [Model Inference](en-us/README.md#model-inference) for the specific steps), ③ adjust the evaluation parameters and click Diagnosis.

- You can switch the metrics to view the model diagnosis results under different parameters. The diagnosis results include mAP, PR curve, precision rate, and recall rate. Examples of the displayed results are as follows.

![idiagnosis_1](https://user-images.githubusercontent.com/90443348/197183853-7039ab7c-cbe5-47c9-9e74-b7e7134bb138.png)

![diagnosis_2](https://user-images.githubusercontent.com/90443348/197184003-1b6328b8-33c7-4da5-879f-0854cdae333f.png)

When looking at the model diagnosis results, you need to think about which metric is more important in the current business scenario, accuracy or recall. Do you want to reduce false positives or false negatives. The former needs to focus more on the precision rate metric, and the latter needs to focus more on the recall rate metric. The evaluation metrics are described as follows.

mAP: mAP (mean average precision) is a metric for measuring the effectiveness of an algorithm in an object detection (Object Detection) algorithm. For the object detection task, each class of object can calculate its precision (Precision) and recall (Recall), multiple calculations/trials at different thresholds, each class can get a P-R curve, can be calculated based on the area under the curve mAP.

Accuracy: The ratio of the number of correctly predicted objects to the total number of predicted objects.

Recall: The ratio of the number of correctly predicted objects to the number of real objects.

## Docker Management

Docker management is an advanced function, currently open only for administrators. Docker management supports users to upload custom dockerimages to achieve the user's ideal training, mining and inference operations. Please refer to [docker development documentation](https://github.com/IndustryEssentials/ymir/tree/master/docker_executor/sample_executor) for specific development standards of dockerimages.

### Add dockerimages

Administrator enter [My Images] page, click [New Image] button, fill in the dockerimage name and address, complete the addition of the dockerimage.

![docker_1](https://user-images.githubusercontent.com/90443348/197184352-cd4ac31c-913e-4d93-a582-60b524addecd.png)

You can also add a dockerimage by copying a public image, enter the [Public Images] page, click the [Copy] button, modify the name and description, and finish copying the public dockerimage.

![docker_2](https://user-images.githubusercontent.com/90443348/197184396-9693de51-e26f-439c-a8f3-20b16502b3cc.png)

### Associated dockerimages

User-defined training, mining and inference dockerimages, in general, need to be associative to ensure that the operational processes can be concatenated. This means that the model trained by the training dockerimage created by user A cannot be adapted to the mining or inference dockerimage created by user B in general. In order to facilitate users to remember the relationship between different categories of dockerimages, the platform has designed a special image association function. Click the [Association] button of the training dockerimage to select the corresponding mining dockerimage.

![docker_3](https://user-images.githubusercontent.com/90443348/197184508-3ca35612-0be8-4cae-8205-ddfa6da1812c.png)

![docker_4](https://user-images.githubusercontent.com/90443348/197184565-d6521722-a65e-4d71-bf92-2cd6daefd0c9.png)

Note: Currently, only training images can be associated with mining images.

## Model Iteration

### Functional Overview

It is difficult to train a model to the best result at one time, and it may be necessary to continuously expand data and tune it by combining model inference results and diagnostic data.

For this reason, we designed the model iteration function. The figure below shows a complete model iteration process, in which the user continuously adjusts the training data and algorithm through multiple iterations, and trains multiple times to obtain better model results.

![workflow](https://user-images.githubusercontent.com/90443348/197184675-4ed1ecdc-e434-4389-a7bf-e55ed55de260.png)

When iteration is enabled, YMIR provides a standardized model iteration process and will help users fill in the previous operation results by default in each step of the operation. If the result of the current operation does not meet your expectation, you can also choose to skip the current operation.

### Function Portal

After creating a project, you can access it by clicking the [Processing models training] button on the [Project Summary] page, or you can access it directly by clicking [Project Iteration] from the left menu operation column under [Project Management].

![iteration_1](https://user-images.githubusercontent.com/90443348/197185933-7b66caf4-3871-4afa-a5fc-a60124ff731f.png)

### Prepare for an iteration

To start an iteration the user needs to prepare the data set to be used and the initial model, the role of each type of data is as follows.

- Training set: the initial data used for training, the categories of the training set need to contain the target categories of the current project. The training set will be continuously expanded during each iteration by means of version updates.

- Mining set: This type of data set is large in number and can not be labeled with the target category yet. When users think there is no more valuable data in the mining set, they can replace it by themselves.

- Validation set: It is used to verify the data during the training process of the model, and the model iteration process uses a unified validation set to participate in the training.
The model iteration process uses a unified validation set to participate in training, which can better compare the model training effect.

- Test set: It is used to test the effect of the model after training, and is generally used in the inference and diagnosis of the model to compare the effect of the model in different data environments.

- Initial model: The model used for mining in the first iteration, which can be imported by the user, and also supports training by the user through the imported training set.

Set up the above data categories separately in the iteration preparation interface, and click the [Use Iteration Function to Enhance Model Effect] button after completion to enter the iteration process.

![Iteration_3](https://user-images.githubusercontent.com/90443348/197186038-345fd500-c5e5-4d8c-91fd-f631219717cd.png)

### Iteration Process

step 1 Preparation of mining data

This operation is used to determine the data to be mined, filter or de-duplicate the data on the selected mining set, and the final result is the data to be mined in the next step, this step can be skipped.

![Iteration_pre_1](https://user-images.githubusercontent.com/90443348/197186246-8414cf84-8da4-444b-8bf4-254a7622b541.png)

step 2 Data Mining

According to the data to be mined obtained in the previous step, set the amount of data that the user wants to mine, other parameters are filled in with the help of the iterative system. Note that the model used for mining here is the final training model obtained from your last iteration (if it is the first iteration, here is the initial model you set), and this step can be skipped after the mining task is completed to get the mining result data.

step 3 Data Annotation

The result after mining usually does not have the label of the target category that the user wants to train, which requires manual labeling of the mining result, click the [Data Label] button in the iterative process to enter the labeling page, the data to be labeled is the mining result in the previous step, other operations refer to [Data Label](en-us/README.md#data-label), this step can be skipped.

step 4 Update the training set

The main purpose of the iteration is to expand the user's training data, merge the already labeled mining results into the previous training set, and generate a new version of the training set for model training.

step 5 Model Training

The merged training set needs to be trained again to generate a new model. Note that the validation set here is the validation set set set by the user before the iteration, which is not supported to be changed for the time being to ensure the consistency of the model effect. Click the [Training] button to get the model results of this iteration.

step 6 Next Iteration

If the result does not meet your requirement, you can click the [Start Next Iteration] button to proceed to the next iteration. The process is the same for each iteration, and you can skip some steps according to your needs.

step7 View Iteration History

After finishing the iteration process, if you need to view the information of the previous or current iteration, you can click the [Iteration History] tab to view the history of the iteration.

![Iteration_history](https://user-images.githubusercontent.com/90443348/197186463-b6b7b08b-ba4f-408f-ad4b-b2fb192894ab.png)

## Model Deployment

For performance and speed reasons, the models generated by the algorithm platform training are not used directly, but are converted to models usable by specific hardware platforms by providing one-click model conversion and quantization tools.

### Local Deployment

step 1 Enter the [Model List] page, click the [Publish] button, and then go to the [Model Deployment] module [My Algorithms] page to check the publishing results after the publishing is finished.

![release_1](https://user-images.githubusercontent.com/90443348/197187385-f8cf6992-c413-4153-b366-2a31a7fd2d08.png)

![release_2](https://user-images.githubusercontent.com/90443348/197187464-0202d0e2-2d5c-401c-97aa-604affdaf284.png)

step 2 Enter the [My Algorithms] page, click the [Deploy] button on the selected released model to enter the [Model Deployment] page, and select the device to be deployed. If you need to select other devices, please go to [Device List] page to add them.

![deploy_1](https://user-images.githubusercontent.com/90443348/197187529-2c0dc73a-4874-4602-9644-5a3405213fa8.png)

![deploy_2](https://user-images.githubusercontent.com/90443348/197187588-d02a330d-9ec9-4fb7-a0de-18e1c3a18909.png)

![deploy_3](https://user-images.githubusercontent.com/90443348/197187612-46df3bde-4dcf-47df-b2e7-b89adda7312a.png)

Step 3 After the deployment is finished, you can go to the device page to check the model operation. Go to the [Device List] page and click the device name to enter the device details page. You can set the status of the algorithm on the [Algorithm Center] page of the device.

![device_1](https://user-images.githubusercontent.com/90443348/197187803-474f491e-0bc3-42b1-aec7-6544cce597df.png)

### Publish to public algorithm library

step 1 Enter the [My Algorithms] page, click the [Publish to Public Algorithm] button for the selected published model, fill in the information and click [OK], then the algorithm will be handed over to the backend for manual review and packaging.

![EN_public_alg_1](https://user-images.githubusercontent.com/90443348/197187965-1e856657-6ea9-445c-b666-4500853cb928.jpg)

![EN_public_alg_2](https://user-images.githubusercontent.com/90443348/197187970-9a5181b5-0c61-47bb-89f6-8967be6a1598.jpg)

![EN_public_alg_3](https://user-images.githubusercontent.com/90443348/197187978-96a68a6b-566e-4724-8e88-d8dcc754faef.jpg)

step 2 After the review, you can go to [Model Deployment] - [Public Algorithm] page to see the corresponding model.

![EN_public_alg_4](https://user-images.githubusercontent.com/90443348/197187982-15b56144-d935-4da2-8504-7a59cafa8a53.jpg)

![EN_public_alg_5](https://user-images.githubusercontent.com/90443348/197187987-7355f29c-fcf7-45f6-a1b7-0df348d5540a.jpg)

step 3 Click the model to enter the algorithm detail page, and you can enter the image URL to try it out.

![EN_public_alg_6](https://user-images.githubusercontent.com/90443348/197187990-5d0aa1cc-c21c-45b6-b85a-c89c6e3d270b.jpg)

![EN_public_alg_7](https://user-images.githubusercontent.com/90443348/197187995-7d268554-5837-4310-b0c3-218bfdf55c64.jpg)

![EN_public_alg_8](https://user-images.githubusercontent.com/90443348/197188000-83bd16c5-06e6-4015-95c6-ffaafc8b5361.jpg)
