# Copyright 2025 Charles Bouquet
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


FROM rapidsai/base:26.02a-cuda13-py3.11 AS backend
# deja installés:
# numpy
# pandas
# pyarrow
# cudf
# dask-cudf
# cuml

USER root

WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Installer les packages Python manquants
RUN pip install --no-cache-dir \
    xlsxwriter \
    matplotlib \
    Pillow \
    fastapi[standard] \
    uvicorn \
    scikit-learn \
    cachetools \
    hdbscan \
    ijson

# Créer le dossier de cache matplotlib
RUN mkdir -p /tmp/matplotlib-cache && \
    chown -R rapids:conda /tmp/matplotlib-cache

# Copier le code et donner les permissions à l'utilisateur rapids
COPY ./backend /app
RUN chown -R rapids:conda /app && chmod 755 -R /app

# Variables d'environnement
ENV MPLCONFIGDIR=/tmp/matplotlib-cache

EXPOSE 8000

# Utiliser l'utilisateur rapids (existant dans l'image)
USER rapids

# L'entrypoint RAPIDS est conservé, on modifie juste la commande
CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

#modifier la ligne pour un serveur http basique
FROM nginx:1.29.4-alpine AS server

WORKDIR /app/nginx
COPY default.conf /etc/nginx/conf.d/default.conf
#donner les permissions à l'utilisateur du conteneur (sinon erreur de permissions au démarrage et pour le fonctionnement)
RUN chown -R nginx:nginx /app/nginx && \
    chown -R nginx:nginx /etc/nginx && \
    chown -R nginx:nginx /var/cache/nginx && \
    chown -R nginx:nginx /var/log/nginx && \
    chown -R nginx:nginx /var/run && \
    chmod 777 /var/run
CMD ["nginx", "-g", "daemon off;"]


FROM node:25-alpine3.22 AS react
WORKDIR /app
#COPY ./frontend /app
COPY ./frontend/package.json /app/
EXPOSE 3000
RUN adduser -S react && addgroup -S react
RUN chown -R react /app && chmod -R 755 /app
RUN chown -R react:react /home/react
RUN mkdir -p /output && chown -R react:react /output

USER react


RUN npm install

#RUN npm run build
#CMD ["npx", "serve", "build", "-p", "3000"] 
CMD ["npm", "start"]