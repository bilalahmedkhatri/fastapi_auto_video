'use client';

import Header from './Header';

const LayoutWrapper = ({ children }) => {
  return (
    <Header>
      {children}
    </Header>
  );
};

export default LayoutWrapper;
