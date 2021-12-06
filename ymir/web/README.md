### YMIR web is an open-source, focusing on ai learning, including training, mining, labelling, all-in-one platform.
## Development
### - Requirement: NodeJS [nodejs website](http://nodejs.cn/) （10.x < version < 17.x）

1. Clone the repository
   ```bash
   git clone https://github.com/IndustryEssentials/ymir.git
   cd ymir
   ```

2. Install required dependencies
   ```bash
   npm install
   ```

3. Config backend app address in .umirc.local.ts, it will be proxy in the same domain automatic.

4. Start the development server
   ```bash
   npm run start
   ```

5. After you make changes and ready to use it in production, you need to create a production build
   ```bash
   npm run build
   ```
   Now you have *.js and *.css files in the `ymir/` directory
## Ecosystem

| Project | Description |
|-|-|
| [ymir](https://github.com/IndustryEssentials/ymir) | Docker images for whole YMIR system. You can install YMIR by one command.|
| ymir-web | Frontend part, written in JavaScript and React |
| [ymir-backend](https://github.com/IndustryEssentials/ymir-backend) | Server backend, supply API, and connect cmd |
| [ymir-cmd](https://github.com/IndustryEssentials/ymir-cmd) | Base, data storage and processing, and open a set of commands for Senior Algorithm Engineer |
