import './globals.css'
import { Inter } from 'next/font/google'

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: 'cncld',
  description: 'app created to check if something is cancelled',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head>
        <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-2367134077911502" crossOrigin='anonymous'></script>
      </head>
      <body className={inter.className}>{children}</body>
    </html>
  )
}
