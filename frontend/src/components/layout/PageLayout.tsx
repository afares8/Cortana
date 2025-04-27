import React from 'react';
import Layout from './Layout';

interface PageLayoutProps {
  children: React.ReactNode;
  title: string;
}

export default function PageLayout({ children, title }: PageLayoutProps) {
  return (
    <Layout title={title}>
      {children}
    </Layout>
  );
}
