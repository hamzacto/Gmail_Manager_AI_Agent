FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application
COPY . .

# Create lib directory and install axios
RUN mkdir -p src/lib && \
    npm install axios && \
    echo "import axios from 'axios'; export default axios;" > src/lib/axios.ts

# Build the application
RUN npm run build

# Expose port 5173 for Vite
EXPOSE 5173

# Start the application
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"] 