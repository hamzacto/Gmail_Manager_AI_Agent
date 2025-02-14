FROM node:18-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy the rest of the application
COPY . .

# Build the application
RUN npm run build

# Expose port 5173 for Vite
EXPOSE 5173

# Use --host 0.0.0.0 to make Vite accessible from outside the container
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"] 