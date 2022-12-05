# World-cup-predictions
In this project, we are going to use statistical analysis and machine learning to build models that can predict the results of a game between football teams
Steps to run:
1. Download [European Soccer Dataset](https://www.kaggle.com/datasets/hugomathien/soccer) and unzip to database folder
2. Run "conda install pytorch torchvision torchaudio pytorch-cuda=11.6 -c pytorch -c nvidia" and "conda install jupyter"
3. Install requirements file  
[Optional] Run the data-preparation.ipynb and upon completion, find the processed dataset in database folder
4. Run the experiments.ipynb  
[NB] The best performing models are saved in the models folder and you can evaluate the models by running the cells below the title "Best Supervised Models Performance evaluation"
5. Scrape world cup rosters by running scrape.py
6. Run 'World Cup Predictions.ipynb'
