pipeline{
    agent any
    stages{
        stage('Cloning from github ......'){
            steps{
                script{
                    echo 'Cloning from github ......'
                    checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'github-token', url: 'https://github.com/mayank3354/Anime-Recommender_deployed_on_GCP.git']])

                }

            }
        
        }
        stage("Making a virtual environment......"){
            steps{
                script{
                    echo 'Making a virtual environment......'
                    sh '''
                    python -m venv ${venv_DIR}
                    source ${venv_DIR}/bin/activate
                    pip install --upgrade pip
                    pip install -e .
                    pip install dvc

                    '''
                }
            }
        }
        stage("DVC PULL"){
            steps{
                withCredentials([file(credentialsId: 'gcp-key1', variable:'GOOGLE_APPLICATION_CREDENTIALS')])
                {
                   script{
                    echo 'DVC Pull..'
                    sh '''
                    . ${venv_DIR}/bin/activate
                    dvc pull
                    '''
                   }
                }
            }
        }
        
    }
}
