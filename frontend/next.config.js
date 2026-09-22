/** @type {import('next').NextConfig} */
const isGithubPages = process.env.BUILD_FOR_GH_PAGES === 'true'
const repoName = 'Resume_Job_Matching_Talent_Marketplace_Engine'

const nextConfig = {
  output: 'export',
  basePath: isGithubPages ? `/${repoName}` : '',
  assetPrefix: isGithubPages ? `/${repoName}/` : '',
  images: {
    unoptimized: true,
  },
  trailingSlash: true,
}

module.exports = nextConfig
