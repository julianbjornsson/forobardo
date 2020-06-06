provider "aws" {
  region  = "us-east-1"
  version = "~> 2.46"
}

variable aws_private_key {
  default = "C:\\Users\\Julian Bjornsson\\aws\\aws_keys\\default-ec2.pem"
}

resource "aws_default_vpc" "default" {
}

####

resource "aws_security_group" "forobardo_sg" {

  name   = "forobardo_sg"
  vpc_id = aws_default_vpc.default.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = -1
    cidr_blocks = ["0.0.0.0/0"]
  }
}

data "aws_subnet_ids" "default_subnets" {
  vpc_id = aws_default_vpc.default.id
}

data "aws_ami" "aws_linux_2_latest" {
  most_recent = true
  owners = ["amazon"]
  filter {
    name = "name"
    values = ["amzn2-ami-hvm-*"]
  }
}

data "aws_ami_ids" "aws-linux-2-latest_ids" {
  owners = ["amazon"]
  filter {
    name = "name"
    values = ["amzn2-ami-hvm-*"]
  }
}

resource "aws_instance" "foroflask" {
  ami                    = data.aws_ami.aws_linux_2_latest.id
  key_name               = "default-ec2"
  instance_type          = "t2.micro"
  vpc_security_group_ids = [aws_security_group.forobardo_sg.id]
  subnet_id              = tolist(data.aws_subnet_ids.default_subnets.ids)[0]
  
  connection {

    type = "ssh"
    host= self.public_ip
    user = "ec2-user"
    private_key = file(var.aws_private_key)
  }
}

