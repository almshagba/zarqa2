#!/bin/bash

# Employee Management System - AWS Deployment Script
# سكريبت نشر نظام إدارة شؤون الموظفين على AWS

set -e  # توقف عند أي خطأ

# الألوان للإخراج
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# دوال المساعدة
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# التحقق من المتطلبات
check_requirements() {
    print_info "التحقق من المتطلبات..."
    
    # التحقق من AWS CLI
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI غير مثبت. يرجى تثبيته أولاً."
        exit 1
    fi
    
    # التحقق من Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker غير مثبت. يرجى تثبيته أولاً."
        exit 1
    fi
    
    # التحقق من EB CLI (اختياري)
    if ! command -v eb &> /dev/null; then
        print_warning "EB CLI غير مثبت. سيتم تخطي نشر Elastic Beanstalk."
        EB_AVAILABLE=false
    else
        EB_AVAILABLE=true
    fi
    
    print_success "تم التحقق من المتطلبات"
}

# قراءة متغيرات البيئة
load_environment() {
    print_info "قراءة متغيرات البيئة..."
    
    if [ -f .env ]; then
        export $(cat .env | grep -v '^#' | xargs)
        print_success "تم تحميل متغيرات البيئة من .env"
    else
        print_warning "ملف .env غير موجود. يرجى إنشاؤه من .env.example"
    fi
    
    # التحقق من المتغيرات المطلوبة
    required_vars=("AWS_ACCESS_KEY_ID" "AWS_SECRET_ACCESS_KEY" "AWS_REGION")
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            print_error "متغير البيئة $var غير محدد"
            exit 1
        fi
    done
}

# إنشاء S3 Bucket
create_s3_bucket() {
    print_info "إنشاء S3 Bucket..."
    
    BUCKET_NAME=${S3_BUCKET:-"employees-system-$(date +%s)"}
    
    if aws s3 ls "s3://$BUCKET_NAME" 2>&1 | grep -q 'NoSuchBucket'; then
        if [ "$AWS_REGION" = "us-east-1" ]; then
            aws s3 mb "s3://$BUCKET_NAME"
        else
            aws s3 mb "s3://$BUCKET_NAME" --region "$AWS_REGION"
        fi
        print_success "تم إنشاء S3 Bucket: $BUCKET_NAME"
    else
        print_info "S3 Bucket موجود بالفعل: $BUCKET_NAME"
    fi
    
    export S3_BUCKET=$BUCKET_NAME
}

# بناء Docker Image
build_docker_image() {
    print_info "بناء Docker Image..."
    
    IMAGE_NAME="employees-system"
    IMAGE_TAG="latest"
    
    docker build -t "$IMAGE_NAME:$IMAGE_TAG" .
    
    print_success "تم بناء Docker Image: $IMAGE_NAME:$IMAGE_TAG"
}

# رفع إلى ECR
push_to_ecr() {
    print_info "رفع Docker Image إلى ECR..."
    
    ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    REPOSITORY_NAME="employees-system"
    ECR_URI="$ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$REPOSITORY_NAME"
    
    # إنشاء ECR repository إذا لم يكن موجوداً
    if ! aws ecr describe-repositories --repository-names "$REPOSITORY_NAME" --region "$AWS_REGION" &> /dev/null; then
        aws ecr create-repository --repository-name "$REPOSITORY_NAME" --region "$AWS_REGION"
        print_success "تم إنشاء ECR repository: $REPOSITORY_NAME"
    fi
    
    # تسجيل الدخول إلى ECR
    aws ecr get-login-password --region "$AWS_REGION" | docker login --username AWS --password-stdin "$ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"
    
    # وضع علامة ورفع الصورة
    docker tag "employees-system:latest" "$ECR_URI:latest"
    docker push "$ECR_URI:latest"
    
    print_success "تم رفع Docker Image إلى ECR: $ECR_URI:latest"
    export ECR_IMAGE_URI="$ECR_URI:latest"
}

# نشر باستخدام Elastic Beanstalk
deploy_elastic_beanstalk() {
    if [ "$EB_AVAILABLE" = false ]; then
        print_warning "تخطي نشر Elastic Beanstalk (EB CLI غير متوفر)"
        return
    fi
    
    print_info "نشر باستخدام Elastic Beanstalk..."
    
    # تهيئة EB إذا لم يكن مهيأً
    if [ ! -f .elasticbeanstalk/config.yml ]; then
        eb init employees-system --region "$AWS_REGION" --platform "Python 3.9" --keyname "$EC2_KEY_PAIR"
    fi
    
    # إنشاء البيئة إذا لم تكن موجودة
    if ! eb list | grep -q "employees-prod"; then
        eb create employees-prod --instance-type t3.micro
    fi
    
    # تعيين متغيرات البيئة
    eb setenv \
        FLASK_ENV=production \
        SECRET_KEY="$SECRET_KEY" \
        DATABASE_URL="$DATABASE_URL" \
        AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
        AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
        S3_BUCKET="$S3_BUCKET"
    
    # النشر
    eb deploy
    
    print_success "تم النشر باستخدام Elastic Beanstalk"
    
    # الحصول على URL التطبيق
    APP_URL=$(eb status | grep "CNAME" | awk '{print $2}')
    print_success "رابط التطبيق: http://$APP_URL"
}

# نشر باستخدام Docker Compose (للاختبار المحلي)
deploy_local() {
    print_info "نشر محلي باستخدام Docker Compose..."
    
    # إنشاء ملف .env للإنتاج
    cat > .env.prod << EOF
FLASK_ENV=production
SECRET_KEY=${SECRET_KEY}
DATABASE_URL=postgresql://postgres:postgres_password@db:5432/employees_db
AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
S3_BUCKET=${S3_BUCKET}
EOF
    
    # تشغيل Docker Compose
    docker-compose -f docker-compose.prod.yml up -d
    
    print_success "تم النشر المحلي. التطبيق متاح على: http://localhost"
}

# تنظيف الموارد
cleanup() {
    print_info "تنظيف الموارد المؤقتة..."
    
    # حذف الصور المحلية القديمة
    docker image prune -f
    
    print_success "تم التنظيف"
}

# عرض المساعدة
show_help() {
    echo "استخدام: $0 [OPTIONS]"
    echo ""
    echo "خيارات النشر:"
    echo "  --local          نشر محلي باستخدام Docker Compose"
    echo "  --aws            نشر على AWS باستخدام Elastic Beanstalk"
    echo "  --ecr-only       رفع Docker Image إلى ECR فقط"
    echo "  --help           عرض هذه المساعدة"
    echo ""
    echo "أمثلة:"
    echo "  $0 --local      # نشر محلي"
    echo "  $0 --aws        # نشر كامل على AWS"
    echo "  $0 --ecr-only   # رفع الصورة إلى ECR فقط"
}

# الدالة الرئيسية
main() {
    print_info "بدء عملية النشر..."
    
    case "$1" in
        --local)
            check_requirements
            load_environment
            build_docker_image
            deploy_local
            ;;
        --aws)
            check_requirements
            load_environment
            create_s3_bucket
            build_docker_image
            push_to_ecr
            deploy_elastic_beanstalk
            cleanup
            ;;
        --ecr-only)
            check_requirements
            load_environment
            build_docker_image
            push_to_ecr
            cleanup
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            print_error "خيار غير صحيح: $1"
            show_help
            exit 1
            ;;
    esac
    
    print_success "انتهت عملية النشر بنجاح!"
}

# تشغيل السكريبت
if [ $# -eq 0 ]; then
    show_help
    exit 1
fi

main "$@"