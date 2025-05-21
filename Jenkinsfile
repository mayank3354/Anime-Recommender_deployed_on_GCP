pipeline {
  agent any

  environment {
    VENV_DIR = 'venv'
  }

  stages {
    stage('Clone') {
      steps {
        checkout scmGit(
          branches: [[name: '*/main']],
          userRemoteConfigs: [[
            credentialsId: 'github-token',
            url: 'https://github.com/mayank3354/Anime-Recommender_deployed_on_GCP.git'
          ]]
        )
      }
    }

    stage('Setup Virtualenv & Dependencies') {
      steps {
        sh '''
          python -m venv ${VENV_DIR}
          . ${VENV_DIR}/bin/activate

          pip install --upgrade pip
          pip install -e .            # your package
          pip install dvc[gcp]        # DVC with GCS support
          pip install --upgrade gcsfs fsspec
          gcloud auth activate-service-account --key-file="$GOOGLE_APPLICATION_CREDENTIALS"
        '''
      }
    }

    stage('DVC Pull') {
      steps {
        withCredentials([file(credentialsId: 'gcp-key1', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
          sh '''
            . ${VENV_DIR}/bin/activate
            dvc pull
          '''
        }
      }
    }
  }
}
