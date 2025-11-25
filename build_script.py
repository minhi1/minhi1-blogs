# A build script that runs shell command to build this blog site.
# Shell command: pnpm build; gh-pages -d dist;

import os

def build_site():
    print("====== Building the site to dist/ folder ======")
    # Run the build command and receive the response
    build_response = os.system("pnpm build")

    if build_response != 0:
        print("Build failed.")
        return
    
    print("====== Deploying the site to GitHub Pages ======")
    # Deploy to GitHub Pages
    deploy_response = os.system("gh-pages -d dist")

    if deploy_response != 0:
        print("Deployment failed.")
        return

build_site()