provider "aws" {
    region = "us-west-1"
}

resource "aws_instance" "devine_ingest" {
    ami           = "ami-0c55b159cbfafe1f0"
    instance_type = "t2.micro"
    vpc_security_group_ids = [aws_security_group.instance.id]

    tags = {
        Name    = "devine_ingest"
        project = "devine"
    }
}

resource "aws_security_group" "instance" {
    name = "devine-http-security"
    ingress {
        from_port   = 80
        to_port     = 80
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }
    ingress {
        from_port   = 443
        to_port     = 443
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }
    ingress {
        from_port   = 22
        to_port     = 22
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }
}

output "public_ip" {
    value       = aws_instance.devine_ingest.public_ip
    description = "The public IP of this ec2 instance"
}

resource "aws_key_pair" "deployer" {
    key_name   = "deployer-key"
    public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDY15NXMjXnXL5sxhyxJZeowV/W0VFLUn72ybxsm11LVqML6JxPvUraVNYqra9tRBdghJ1wQ/MV1qweeX0tkcwFCJYwl+2STpaTJigsQnd3l2G4GnvWPOB9d4FLBJGjtsROIQ70kvcd3c20HWZZ1F4mG81RIFy95qbjkSKht+StapTut2h1ymUZQk197GQhR6RUcktXA7LZgFbxOHGRtzK7ZIhKFG761SFZAptn9YbWVbwTTrcwAMoTZhYLFHkO1RSJChVwSzxu34nfB6CQT0G7sfR+oYgzQ6IqVxxtOdU5Z1Ay8TCY5Ogo+qgAExqWr4Im3zUsVEuKBj/waT/z7RXr"
}