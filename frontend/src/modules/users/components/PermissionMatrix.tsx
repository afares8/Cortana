import React, { useState, useEffect } from 'react';
import { Checkbox } from "../../../components/ui/checkbox";
import { Label } from "../../../components/ui/label";
import { Button } from "../../../components/ui/button";
import { Calendar } from "../../../components/ui/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "../../../components/ui/popover";
import { format } from "date-fns";
import { CalendarIcon } from "lucide-react";
import { cn } from "../../../lib/utils";
import { Permission } from '../types';
import { useTranslation } from 'react-i18next';

interface PermissionMatrixProps {
  permissions: Permission[];
  selectedPermissions: { id: number; start_date?: Date; end_date?: Date }[];
  onChange: (selectedPermissions: { id: number; start_date?: Date; end_date?: Date }[]) => void;
}

type ModuleMap = {
  [key: string]: {
    label: string;
    actions: {
      [key: string]: {
        id: number;
        label: string;
      }
    }
  }
};

const PermissionMatrix: React.FC<PermissionMatrixProps> = ({ 
  permissions, 
  selectedPermissions, 
  onChange 
}) => {
  const { t } = useTranslation();
  const [moduleMap, setModuleMap] = useState<ModuleMap>({});
  const [dates, setDates] = useState<{ [key: number]: { start?: Date; end?: Date } }>({});
  
  useEffect(() => {
    const map: ModuleMap = {};
    
    permissions.forEach(permission => {
      if (!map[permission.module]) {
        map[permission.module] = {
          label: permission.module.charAt(0).toUpperCase() + permission.module.slice(1),
          actions: {}
        };
      }
      
      map[permission.module].actions[permission.action] = {
        id: permission.id,
        label: permission.action.charAt(0).toUpperCase() + permission.action.slice(1)
      };
    });
    
    setModuleMap(map);
    
    const initialDates: { [key: number]: { start?: Date; end?: Date } } = {};
    selectedPermissions.forEach(perm => {
      initialDates[perm.id] = {
        start: perm.start_date ? new Date(perm.start_date) : undefined,
        end: perm.end_date ? new Date(perm.end_date) : undefined
      };
    });
    setDates(initialDates);
  }, [permissions, selectedPermissions]);
  
  const isSelected = (permissionId: number) => {
    return selectedPermissions.some(p => p.id === permissionId);
  };
  
  const handlePermissionToggle = (permissionId: number) => {
    let newSelectedPermissions;
    
    if (isSelected(permissionId)) {
      newSelectedPermissions = selectedPermissions.filter(p => p.id !== permissionId);
    } else {
      const dateInfo = dates[permissionId] || {};
      newSelectedPermissions = [
        ...selectedPermissions,
        { 
          id: permissionId, 
          start_date: dateInfo.start, 
          end_date: dateInfo.end 
        }
      ];
    }
    
    onChange(newSelectedPermissions);
  };
  
  const handleDateChange = (permissionId: number, type: 'start' | 'end', date?: Date) => {
    setDates(prev => ({
      ...prev,
      [permissionId]: {
        ...prev[permissionId],
        [type]: date
      }
    }));
    
    if (isSelected(permissionId)) {
      const newSelectedPermissions = selectedPermissions.map(p => {
        if (p.id === permissionId) {
          return {
            ...p,
            start_date: type === 'start' ? date : p.start_date,
            end_date: type === 'end' ? date : p.end_date
          };
        }
        return p;
      });
      
      onChange(newSelectedPermissions);
    }
  };
  
  return (
    <div className="space-y-6">
      <h3 className="text-lg font-medium">{t('Permissions')}</h3>
      
      {Object.entries(moduleMap).map(([moduleName, moduleData]) => (
        <div key={moduleName} className="border rounded-md p-4">
          <h4 className="font-medium mb-2">{t(moduleData.label)}</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(moduleData.actions).map(([actionName, actionData]) => {
              const permissionId = actionData.id;
              const dateInfo = dates[permissionId] || {};
              
              return (
                <div key={actionName} className="space-y-2">
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id={`permission-${permissionId}`}
                      checked={isSelected(permissionId)}
                      onCheckedChange={() => handlePermissionToggle(permissionId)}
                    />
                    <Label htmlFor={`permission-${permissionId}`}>
                      {t(actionData.label)}
                    </Label>
                  </div>
                  
                  {isSelected(permissionId) && (
                    <div className="pl-6 grid grid-cols-1 gap-2">
                      <div className="flex items-center space-x-2">
                        <Label htmlFor={`start-date-${permissionId}`} className="text-xs">
                          {t('Start Date')}:
                        </Label>
                        <Popover>
                          <PopoverTrigger asChild>
                            <Button
                              id={`start-date-${permissionId}`}
                              variant="outline"
                              size="sm"
                              className={cn(
                                "w-[130px] justify-start text-left text-xs",
                                !dateInfo.start && "text-muted-foreground"
                              )}
                            >
                              <CalendarIcon className="mr-2 h-3 w-3" />
                              {dateInfo.start ? format(dateInfo.start, "PPP") : t('Optional')}
                            </Button>
                          </PopoverTrigger>
                          <PopoverContent className="w-auto p-0">
                            <Calendar
                              mode="single"
                              selected={dateInfo.start}
                              onSelect={(date) => handleDateChange(permissionId, 'start', date)}
                              initialFocus
                            />
                          </PopoverContent>
                        </Popover>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        <Label htmlFor={`end-date-${permissionId}`} className="text-xs">
                          {t('End Date')}:
                        </Label>
                        <Popover>
                          <PopoverTrigger asChild>
                            <Button
                              id={`end-date-${permissionId}`}
                              variant="outline"
                              size="sm"
                              className={cn(
                                "w-[130px] justify-start text-left text-xs",
                                !dateInfo.end && "text-muted-foreground"
                              )}
                            >
                              <CalendarIcon className="mr-2 h-3 w-3" />
                              {dateInfo.end ? format(dateInfo.end, "PPP") : t('Optional')}
                            </Button>
                          </PopoverTrigger>
                          <PopoverContent className="w-auto p-0">
                            <Calendar
                              mode="single"
                              selected={dateInfo.end}
                              onSelect={(date) => handleDateChange(permissionId, 'end', date)}
                              initialFocus
                            />
                          </PopoverContent>
                        </Popover>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
};

export default PermissionMatrix;
