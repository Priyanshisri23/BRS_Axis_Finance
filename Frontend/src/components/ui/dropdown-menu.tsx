import React, { useState, useRef, useEffect } from 'react';
import { createPortal } from 'react-dom';

interface DropdownMenuProps {
  children: React.ReactNode;
}

interface DropdownMenuTriggerProps {
  children: React.ReactNode;
  asChild?: boolean;
}

interface DropdownMenuContentProps {
  children: React.ReactNode;
}

interface DropdownMenuItemProps {
  onSelect?: () => void;
  children: React.ReactNode;
}

const DropdownMenuContext = React.createContext<{
  isOpen: boolean;
  setIsOpen: React.Dispatch<React.SetStateAction<boolean>>;
  triggerRef: React.RefObject<HTMLElement>;
}>({
  isOpen: false,
  setIsOpen: () => {},
  triggerRef: { current: null },
});

const DropdownMenu: React.FC<DropdownMenuProps> & {
  Trigger: React.FC<DropdownMenuTriggerProps>;
  Content: React.FC<DropdownMenuContentProps>;
} = ({ children }) => {
  const [isOpen, setIsOpen] = useState(false);
  const triggerRef = useRef<HTMLElement>(null);

  return (
    <DropdownMenuContext.Provider value={{ isOpen, setIsOpen, triggerRef }}>
      {children}
    </DropdownMenuContext.Provider>
  );
};

const DropdownMenuTrigger: React.FC<DropdownMenuTriggerProps> = ({ children, asChild }) => {
  const { setIsOpen, triggerRef } = React.useContext(DropdownMenuContext);

  const handleClick = () => {
    setIsOpen((prev) => !prev);
  };

  if (asChild) {
    return React.cloneElement(children as React.ReactElement, {
      onClick: handleClick,
      ref: triggerRef,
    });
  }

  return (
    <button onClick={handleClick} ref={triggerRef as React.RefObject<HTMLButtonElement>}>
      {children}
    </button>
  );
};

const DropdownMenuContent: React.FC<DropdownMenuContentProps> = ({ children }) => {
  const { isOpen, setIsOpen, triggerRef } = React.useContext(DropdownMenuContext);
  const contentRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        contentRef.current &&
        !contentRef.current.contains(event.target as Node) &&
        triggerRef.current &&
        !triggerRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [setIsOpen, triggerRef]);

  if (!isOpen) return null;

  return createPortal(
    <div
      ref={contentRef}
      className="absolute z-10 mt-2 w-56 rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none"
      style={{
        top: triggerRef.current ? triggerRef.current.getBoundingClientRect().bottom + window.scrollY : 0,
        left: triggerRef.current ? triggerRef.current.getBoundingClientRect().left + window.scrollX : 0,
      }}
    >
      <div className="py-1" role="menu" aria-orientation="vertical" aria-labelledby="options-menu">
        {children}
      </div>
    </div>,
    document.body
  );
};

export const DropdownMenuItem: React.FC<DropdownMenuItemProps> = ({ onSelect, children }) => {
  const { setIsOpen } = React.useContext(DropdownMenuContext);

  const handleClick = () => {
    if (onSelect) {
      onSelect();
    }
    setIsOpen(false);
  };

  return (
    <button
      className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 hover:text-gray-900"
      role="menuitem"
      onClick={handleClick}
    >
      {children}
    </button>
  );
};

DropdownMenu.Trigger = DropdownMenuTrigger;
DropdownMenu.Content = DropdownMenuContent;

export default DropdownMenu;