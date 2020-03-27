provider "aws" {
    region = "us-west-1"
}

resource "aws_instance" "devine_ingest" {
    ami           = "ami-03ba3948f6c37a4b0"
    instance_type = "t2.micro"
    vpc_security_group_ids = [aws_security_group.instance.id]
    key_name   = "ci.manager.deployer"

    tags = {
        Name    = "devine_ingest"
        project = "devine"
    }
}

resource "aws_security_group" "instance" {
    name = "devine-ingest-security"
    ingress {
        from_port   = 80
        to_port     = 80
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }
    egress {
        from_port   = 0
        to_port     = 0
        protocol    = "-1"
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
    key_name   = "ci.manager.deployer"
    public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC9kWXFQEvxaQw7BizPXJK1TnAEsi16p0T4RsVUBTY3JKZmpg0zYg/y8iWQn4f3InIIxgC6hsmGC0zihbF25mg4tBVsh1coRl+RC6O28JapRfB3fSJck7soTAg2ABY59LlHVV0D9JhZwWCO6d8sH5M7+Kh0poXJDwsSt15vpb99RsIAKRoQDXCTvKy71kF0Jcw1yA/Q/NbtDaxz7FTBwTECwspjpyZdwNf6FFTNgO/WxS593Fqdp2XFJ3rxOGMEFQWta5zNdfFj2jeKrFkKwUyLKDs3Yxt1XpW44OuascKDoMnbQ0nQYksBphA8J2UMnCPCyOfNLCPXZiVdf2LjtwJB"
}