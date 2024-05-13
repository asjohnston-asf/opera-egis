FROM ghcr.io/lambgeo/lambda-gdal:3.8 as gdal

# This example assume that you are creating a lambda package for python 3.10
FROM public.ecr.aws/lambda/python:3.10

RUN  yum clean all && yum -y update && yum -y install gcc gcc-c++ unzip curl zip

# Bring C libs from lambgeo/lambda-gdal image
COPY --from=gdal /opt/lib/ /opt/lib/
COPY --from=gdal /opt/include/ /opt/include/
COPY --from=gdal /opt/share/ /opt/share/
COPY --from=gdal /opt/bin/ /opt/bin/

ENV \
  GDAL_DATA=/opt/share/gdal \
  PROJ_LIB=/opt/share/proj \
  GDAL_CONFIG=/opt/bin/gdal-config \
  GEOS_CONFIG=/opt/bin/geos-config \
  PATH=/opt/bin:$PATH

ENV PACKAGE_PREFIX=/var/task

# Copy local files
COPY main.py ${PACKAGE_PREFIX}/main.py

# install package
# This example shows how to install GDAL python bindings for gdal 3.6
# The GDAL version should be the same as the one provided by the `lambgeo/lambda-gdal` image
RUN python -m pip install GDAL==$(gdal-config --version) -t $PACKAGE_PREFIX
RUN python -m pip install requests -t $PACKAGE_PREFIX
RUN python -m pip install boto3 -t $PACKAGE_PREFIX

# Create package.zip
RUN cd $PACKAGE_PREFIX && zip -r9q /tmp/package.zip *
