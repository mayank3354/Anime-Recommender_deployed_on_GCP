pipeline {
  agent any

  environment {
    VENV_DIR           = 'venv'
    GCP_PROJECT        = 'clear-shadow-456404-i1'
    GCLOUD_PATH        = "/var/jenkins_home/google-cloud-sdk/bin"
    KUBECTL_AUTH_PLUGIN = "/usr/lib/google-cloud-sdk/bin"
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

    stage('Build and Push Image to GCR') {
      steps {
        withCredentials([file(credentialsId: 'gcp-key1', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
          sh '''
            export PATH=$PATH:${GCLOUD_PATH}
            gcloud auth activate-service-account --key-file="${GOOGLE_APPLICATION_CREDENTIALS}"
            gcloud config set project ${GCP_PROJECT}
            gcloud auth configure-docker --quiet
            docker build -t gcr.io/${GCP_PROJECT}/anime-recommender:latest .
            docker push gcr.io/${GCP_PROJECT}/anime-recommender:latest
          '''
        }
      }
    }

    stage('Deploying to Kubernetes') {
      steps {
        withCredentials([file(credentialsId: 'gcp-key1', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
          sh '''
            export PATH=$PATH:${GCLOUD_PATH}:${KUBECTL_AUTH_PLUGIN}
            gcloud auth activate-service-account --key-file="${GOOGLE_APPLICATION_CREDENTIALS}"
            gcloud config set project ${GCP_PROJECT}
            gcloud container clusters get-credentials ml-app-cluster1 --region us-central1
            kubectl apply -f deployment.yml
          '''
        }
      }
    }
  }
}
