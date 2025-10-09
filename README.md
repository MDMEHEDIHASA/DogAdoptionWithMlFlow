# Dog Adoption ML Project
## An MLOps Project for the [ZenML Month of MLOps Competition]
mlops_project/
│
├── data/
│   └── raw/                 ← your original images.zip goes here
│
├── src/
│   ├── steps/
│   │   ├── data_divider.py   ← load, unzip, and split dataset
│   │   ├── train_model.py
│   │   └── evaluate_model.py
│   ├── pipelines/
│   │   └── training_pipeline.py
│   └── utils/
│       └── helpers.py
│
├── requirements.txt
├── zenml_config.yaml
└── README.md
