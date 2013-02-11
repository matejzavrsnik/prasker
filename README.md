####
Prasker
####
Prasker 1.0
1-Jan-2012

************
Introduction
************

Prasker is a python script, that parses visible text from html pages.
At the moment, Prasker supports:

* Compute

  * Amazon Elastic Compute Cloud (EC2)
  * Amazon Elastic Map Reduce (EMR)
  * AutoScaling
  * Elastic Load Balancing (ELB)

* Content Delivery

  * Amazon CloudFront

* Database

  * Amazon Relational Data Service (RDS)
  * Amazon DynamoDB
  * Amazon SimpleDB

* Deployment and Management

  * AWS Identity and Access Management (IAM)
  * Amazon CloudWatch
  * AWS Elastic Beanstalk
  * AWS CloudFormation

* Application Services

  * Amazon CloudSearch
  * Amazon Simple Workflow Service (SWF)
  * Amazon Simple Queue Service (SQS)
  * Amazon Simple Notification Server (SNS)
  * Amazon Simple Email Service (SES)

* Networking

  * Amazon Route53
  * Amazon Virtual Private Cloud (VPC)

* Payments and Billing

  * Amazon Flexible Payment Service (FPS)

* Storage

  * Amazon Simple Storage Service (S3)
  * Amazon Glacier
  * Amazon Elastic Block Store (EBS)
  * Google Cloud Storage

* Workforce

  * Amazon Mechanical Turk

* Other

  * Marketplace Web Services

The goal of boto is to support the full breadth and depth of Amazon
Web Services.  In addition, boto provides support for other public
services such as Google Storage in addition to private cloud systems
like Eucalyptus, OpenStack and Open Nebula.

Boto is developed mainly using Python 2.6.6 and Python 2.7.1 on Mac OSX
and Ubuntu Maverick.  It is known to work on other Linux distributions
and on Windows.  Boto requires no additional libraries or packages
other than those that are distributed with Python.  Efforts are made
to keep boto compatible with Python 2.5.x but no guarantees are made.

************
Installation
************

Currently it doesn't install. It is used directly from console.

**********
ChangeLogs
**********

This is the first version.

*************************
Getting Started with Boto
*************************

Your credentials can be passed into the methods that create
connections.  Alternatively, boto will check for the existance of the
following environment variables to ascertain your credentials:

**AWS_ACCESS_KEY_ID** - Your AWS Access Key ID

**AWS_SECRET_ACCESS_KEY** - Your AWS Secret Access Key

Credentials and other boto-related settings can also be stored in a
boto config file.  See `this`_ for details.

Copyright (c) 2006-2012 Mitch Garnaat <mitch@garnaat.com>
Copyright (c) 2010-2011, Eucalyptus Systems, Inc.
Copyright (c) 2012 Amazon.com, Inc. or its affiliates.
All rights reserved.

.. _pip: http://www.pip-installer.org/
.. _release notes: https://github.com/boto/boto/wiki
.. _github.com: http://github.com/boto/boto
.. _Online documentation: http://docs.pythonboto.org
.. _Python Cheese Shop: http://pypi.python.org/pypi/boto
.. _this: http://code.google.com/p/boto/wiki/BotoConfig
.. _gitflow: http://nvie.com/posts/a-successful-git-branching-model/
.. _neo: https://github.com/boto/boto/tree/neo
.. _boto-users Google Group: https://groups.google.com/forum/?fromgroups#!forum/boto-users