### YMIR web is an open-source, focusing on ai learning, including training, mining, labelling, all-in-one platform.
## Development
### - Requirement: NodeJS [nodejs website](http://nodejs.cn/) （10.x < version <= 16.x）

1. Clone the repository
   ```bash
   git clone https://github.com/IndustryEssentials/ymir.git
   cd ymir/ymir/web
   ```

2. Install required dependencies
   ```bash
   yarn install
   ```

3. Config backend app address in .umirc.local.ts, it will be proxy in the same domain automatic.

4. Start the development server
   ```bash
   yarn run start
   ```

5. After you make changes and ready to use it in production, you need to create a production build
   ```bash
   yarn run build
   ```
   Now you have *.js and *.css files in the `ymir/` directory
