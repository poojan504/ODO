This folder contains the code required to generate poems.
poem_generator_training_haiku.ipynb contains the code to train the poem generator. 
Steps to train the poem generator:
1. Open this file in Google colab. 
2. Set environment to be Python3 and GPU. 
3. Click on Runtime->Run all
4. This will take time to train. 4-5 hours. Inorder to reduce the train time, reduce the epochs in section [17].
5. After training is complete, a new folder will be create in colab wthe name "output_all_data". 
6. Create a folder named trained_models in this path. Copy the .hdf5 and metadata.pkl files to trained_models.
6. Rename the .hdf5 file to "poem_generator_weights.hdf5"

After the above steps, this module is built and ready to be used by odo chatbot.
