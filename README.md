
# Leads Management UI

Leads Management UI is a comprehensive web application designed to manage leads effectively. It integrates with Google SSO and Google Drive APIs to offer a seamless and efficient user experience. The application is built using Python, Django, PostgreSQL, Docker, and AWS services.

## Features

- **User Authentication**: Secure login with Google SSO.
- **Lead Management**: Create, read, update, and delete leads.
- **Google Drive Integration**: Sync leads data with Google Drive and Docs.
- **Secure Storage**: Store leads information securely in a PostgreSQL database.
- **Scalable Deployment**: Deploy on AWS ECS and EC2 with PostgreSQL compatibility and KMS Secrets Manager.

## Technologies Used

- **Backend**: Python, Django
- **Frontend**: HTML, CSS, JavaScript
- **Database**: PostgreSQL
- **Authentication**: Google SSO
- **Integration**: Google Drive API, Google Docs API
- **Deployment**: Docker, AWS ECS, EC2, AWS Aurora (Postgres compatibility), AWS KMS

## Getting Started

### Prerequisites

- Python 3.x
- Docker
- AWS account with necessary permissions
- Google Cloud Platform account for API access

### Installation

#### Prerequisites

1. **Google Console Project Setup**:
    - Set up a project on the [Google Cloud Console](https://console.cloud.google.com/).
    - Enable the Google Drive and Google Docs APIs.
    - Create OAuth 2.0 Client IDs for web applications to get your `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`.
    - Follow the instructions provided by the [django-allauth library](https://django-allauth.readthedocs.io/en/latest/providers.html#google) to configure Google OAuth.

2. **AWS Account**:
    - Create an ECR repository named `leads-management`.
    - Ensure you have an S3 bucket for storing deployment configurations.
    - Ensure you have the necessary IAM roles and policies.

#### Local Setup

1. **Clone the repository**:
    ```bash
    git clone https://github.com/YourUsername/Leads-Management-UI.git
    cd Leads-Management-UI
    ```

2. **Set up a virtual environment**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Set up environment variables**:
    - Create a `.env` file in the project root and add the following environment variables:
    ```env
    GOOGLE_CLIENT_ID=your_google_client_id
    GOOGLE_CLIENT_SECRET=your_google_client_secret
    GOOGLE_API_KEY=your_google_api_key
    AWS_ACCESS_KEY_ID=your_aws_access_key_id
    AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
    DATABASE_URL=your_database_url
    ```

5. **Run the Django migrations**:
    ```bash
    python manage.py migrate
    ```

6. **Start the development server**:
    ```bash
    python manage.py runserver
    ```

### Docker Deployment

1. **Build the Docker image**:
    ```bash
    docker build -t leads-management-ui .
    ```

2. **Run the Docker container**:
    ```bash
    docker run -p 8000:8000 --env-file .env leads-management-ui
    ```

### Docker Deployment

1. **Build the Docker image**:
    ```bash
    docker build -t leads-management-ui .
    ```

2. **Run the Docker container**:
    ```bash
    docker run -p 8000:8000 --env-file .env leads-management-ui
    ```

### AWS Deployment

This project uses GitHub Actions to automate the deployment process to AWS ECS. Follow these steps to set up and deploy the application:

1. **Fork the repository**: 
    ```bash
    git clone https://github.com/YourUsername/Leads-Management-UI.git
    cd Leads-Management-UI
    ```

2. **Set up AWS Resources**:
    - Create an ECR repository named `leads-management`.
    - Ensure you have an S3 bucket for storing deployment configurations.
    - Ensure you have the necessary IAM roles and policies.

3. **Populate GitHub Secrets**:
    - Go to your GitHub repository.
    - Navigate to **Settings > Secrets and variables > Actions**.
    - Add the following secrets:
        - `AWS_ACCESS_KEY_ID`: Your AWS Access Key ID.
        - `AWS_SECRET_ACCESS_KEY`: Your AWS Secret Access Key.
        - `DBKMSKEYID`: Your AWS KMS Key ID for database encryption.
        - `BUCKET_NAME`: The name of your S3 bucket for deployment files.
        - `DEPLOYMENTS_PATH`: The path within your S3 bucket for deployment files.

4. **Populate GitHub Variables**:
    - Go to your GitHub repository.
    - Navigate to **Settings > Secrets and variables > Actions**.
    - Add the following variables:
        - `AWS_REGION`: Your preferred AWS region, e.g., `ap-south-1`.

5. **GitHub Actions Workflow**:
    - The GitHub Actions workflow is defined in the file located at `<repo root>/.github/workflows/deploy.yml`.
    - This workflow will automatically build and deploy your application to AWS ECS on every push to the `wip` or `master` branch.

### GitHub Actions Workflow

The workflow performs the following steps:

- **Check out code**: Checks out the code from the repository.
- **Configure AWS credentials**: Configures AWS credentials using IAM role for GitHub Actions.
- **Login to Amazon ECR**: Logs into Amazon ECR.
- **Sync AWS deployment config files**: Syncs deployment configuration files to S3.
- **Ensure ECR Repository**: Ensures the ECR repository exists using CloudFormation.
- **Build, tag, and push image to Amazon ECR**: Builds the Docker image, tags it, and pushes it to Amazon ECR.
- **Deploy CloudFormation stack**: Deploys the CloudFormation stack using the parameters and template stored in S3.

### Example `deploy.yml`

```yaml
name: Build and Deploy to ECS

on:
  push:
    branches:
      - wip
      - master
env:
  AWS_REGION: ap-south-1                   # set this to your preferred AWS region, e.g. us-west-1
  ECR_REPOSITORY: leads-management           # set this to your Amazon ECR repository name
  ECS_TASK_DEFINITION: ./.aws/task-definition.json
  CONTAINER_NAME: ${{ github.event.repository.name }}
  PROJECT_NAME: ${{ github.event.repository.name }}
  PROJECT_DEPLOYMENTS_S3_URL: https://${{ vars.BUCKET_NAME }}.s3.${{ vars.AWS_REGION }}.amazonaws.com/${{ vars.DEPLOYMENTS_PATH }}/${{ github.event.repository.name }}

permissions:
  id-token: write # required to use OIDC authentication
  contents: read # required to checkout the code from the repo

jobs:
  build:
    name: Build Image
    runs-on: ubuntu-latest

    steps:
      - name: Check out code
        uses: actions/checkout@v3.3.0
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          role-to-assume: arn:aws:iam::129190006344:role/Github-Actions
          role-duration-seconds: 900 # the ttl of the session, in seconds.
          aws-region: ap-south-1 # use your region here.

      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v1

      - name: Sync AWS deployment config files
        id: sync-deployment-files
        run: |
          aws s3 sync .aws/ s3://${{ vars.BUCKET_NAME }}/${{ vars.DEPLOYMENTS_PATH }}/${{ env.PROJECT_NAME }}

      - name: Ensure ECR Repository
        id: ensure-ecr-repository
        uses: aws-actions/aws-cloudformation-github-deploy@v1
        with:
          name: ecr-repository-${{ env.PROJECT_NAME }}
          template: ${{ env.PROJECT_DEPLOYMENTS_S3_URL }}/cf/ecr.yaml
          parameter-overrides: RepositoryName=${{ env.ECR_REPOSITORY }}
          no-fail-on-empty-changeset: "1"
          termination-protection: "1"

      - name: Build, tag, and push image to Amazon ECR
        id: build-image
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          ECR_REPOSITORY: ${{ steps.ensure-ecr-repository.outputs.RepositoryUri }}
          IMAGE_TAG: ${{ github.sha }}
        run: |
          # Build a docker container and
          # push it to ECR so that it can
          # be deployed to ECS.
          docker build -t $ECR_REPOSITORY:$IMAGE_TAG .
          docker push $ECR_REPOSITORY:$IMAGE_TAG
          echo "image=$ECR_REPOSITORY:$IMAGE_TAG" >> $GITHUB_OUTPUT

      - name: Deploy cloudformation stack
        id: deploy-cloudformation-stack
        uses: aws-actions/aws-cloudformation-github-deploy@v1
        with:
          name: ${{ env.PROJECT_NAME }}-stack
          template: ${{ env.PROJECT_DEPLOYMENTS_S3_URL }}/${{ vars.DEPLOYMENTS_PATH }}/${{ env.PROJECT_NAME }}/cf/master.yaml
          parameter-overrides: ProjectName=${{ env.PROJECT_NAME }},ECRImage=${{ steps.build-image.outputs.image }},DbKmsKeyId=${{secrets.DBKMSKEYID}},ProjectDeploymentsS3Url=${{ env.PROJECT_DEPLOYMENTS_S3_URL }}
          no-fail-on-empty-changeset: "1"
          termination-protection: "1"
```

This setup ensures that your application is automatically built, tagged, pushed to ECR, and deployed to ECS whenever changes are pushed to the specified branches. Adjust the IAM role ARN and other variables according to your setup.


## Usage

1. **Login**: Use your Google account to log in.
2. **Manage Leads**: Add, view, update, and delete leads.
3. **Sync with Google Drive**: Automatically sync your leads data with Google Drive and Docs for easy access and sharing.

## Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature`).
3. Commit your changes (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Create a new Pull Request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- Thanks to [Google Cloud Platform](https://cloud.google.com/) for providing robust APIs.
- Special thanks to [AWS](https://aws.amazon.com/) for their cloud services.

---