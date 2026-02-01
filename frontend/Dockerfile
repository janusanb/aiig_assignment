FROM node:20-alpine

WORKDIR /app

ENV VITE_API_URL=http://localhost:8000

COPY package.json package-lock.json ./
RUN npm ci

COPY index.html vite.config.ts tsconfig.json tsconfig.node.json ./
COPY src/ ./src/

EXPOSE 5173

CMD ["npm", "run", "dev"]
