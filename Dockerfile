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

FROM python:3.14.2-slim AS backend
WORKDIR /app
COPY ./backend /app
EXPOSE 8000
RUN pip install --no-cache-dir pandas xlsxwriter matplotlib numpy Pillow fastapi[standard] uvicorn

RUN adduser --system --group python
RUN chown -R python:python /app && chmod 755 -R /app
USER python
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