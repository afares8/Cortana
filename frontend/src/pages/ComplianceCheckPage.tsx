import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import { ComplianceCheck } from '../components/compliance/ComplianceCheck';

interface Person {
  name: string;
  dob: string;
  country: string;
}

const ComplianceCheckPage: React.FC = () => {
  const { t } = useTranslation();
  const [customerType, setCustomerType] = useState<'natural' | 'legal'>('natural');
  const [customerName, setCustomerName] = useState('');
  const [customerDob, setCustomerDob] = useState('');
  const [customerCountry, setCustomerCountry] = useState('');
  const [directors, setDirectors] = useState<Person[]>([]);
  const [ubos, setUbos] = useState<Person[]>([]);
  const [showForm, setShowForm] = useState(true);

  const addDirector = () => {
    setDirectors([...directors, { name: '', dob: '', country: '' }]);
  };

  const updateDirector = (index: number, field: keyof Person, value: string) => {
    const updatedDirectors = [...directors];
    updatedDirectors[index] = { ...updatedDirectors[index], [field]: value };
    setDirectors(updatedDirectors);
  };

  const removeDirector = (index: number) => {
    setDirectors(directors.filter((_, i) => i !== index));
  };

  const addUbo = () => {
    setUbos([...ubos, { name: '', dob: '', country: '' }]);
  };

  const updateUbo = (index: number, field: keyof Person, value: string) => {
    const updatedUbos = [...ubos];
    updatedUbos[index] = { ...updatedUbos[index], [field]: value };
    setUbos(updatedUbos);
  };

  const removeUbo = (index: number) => {
    setUbos(ubos.filter((_, i) => i !== index));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setShowForm(false);
  };

  const handleReset = () => {
    setShowForm(true);
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">
          {t('compliance.customerVerification')}
        </h1>
      </div>

      {showForm ? (
        <Card>
          <CardHeader>
            <CardTitle>{t('compliance.customerInformation')}</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Customer Type Selection */}
              <div className="space-y-2">
                <Label>{t('compliance.customerType')}</Label>
                <Select 
                  value={customerType} 
                  onValueChange={(value: 'natural' | 'legal') => {
                    setCustomerType(value);
                    if (value === 'natural') {
                      setDirectors([]);
                      setUbos([]);
                    }
                  }}
                >
                  <SelectTrigger>
                    <SelectValue placeholder={t('compliance.selectCustomerType')} />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="natural">{t('compliance.naturalPerson')}</SelectItem>
                    <SelectItem value="legal">{t('compliance.legalEntity')}</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Customer Basic Information */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="customerName">{t('compliance.name')}</Label>
                  <Input 
                    id="customerName" 
                    value={customerName}
                    onChange={(e) => setCustomerName(e.target.value)}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="customerCountry">{t('compliance.country')}</Label>
                  <Input 
                    id="customerCountry" 
                    value={customerCountry}
                    onChange={(e) => setCustomerCountry(e.target.value)}
                    required
                  />
                </div>
              </div>

              {/* Date of Birth (for natural persons only) */}
              {customerType === 'natural' && (
                <div className="space-y-2">
                  <Label htmlFor="customerDob">{t('compliance.dateOfBirth')}</Label>
                  <Input 
                    id="customerDob" 
                    placeholder="YYYY-MM-DD"
                    value={customerDob}
                    onChange={(e) => setCustomerDob(e.target.value)}
                  />
                </div>
              )}

              {/* Directors (for legal entities only) */}
              {customerType === 'legal' && (
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <Label>{t('compliance.directors')}</Label>
                    <Button 
                      type="button" 
                      variant="secondary"
                      onClick={addDirector}
                    >
                      {t('compliance.addDirector')}
                    </Button>
                  </div>
                  
                  {directors.map((director, index) => (
                    <Card key={index}>
                      <CardContent className="pt-6">
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                          <div className="space-y-2">
                            <Label>{t('compliance.name')}</Label>
                            <Input 
                              value={director.name}
                              onChange={(e) => updateDirector(index, 'name', e.target.value)}
                              required
                            />
                          </div>
                          <div className="space-y-2">
                            <Label>{t('compliance.dateOfBirth')}</Label>
                            <Input 
                              type="date"
                              value={director.dob}
                              onChange={(e) => updateDirector(index, 'dob', e.target.value)}
                              required
                            />
                          </div>
                          <div className="space-y-2">
                            <Label>{t('compliance.country')}</Label>
                            <Input 
                              value={director.country}
                              onChange={(e) => updateDirector(index, 'country', e.target.value)}
                              required
                            />
                          </div>
                        </div>
                        <Button 
                          type="button" 
                          variant="destructive"
                          className="mt-4"
                          onClick={() => removeDirector(index)}
                        >
                          {t('compliance.remove')}
                        </Button>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}

              {/* UBOs (for legal entities only) */}
              {customerType === 'legal' && (
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <Label>{t('compliance.ubos')}</Label>
                    <Button 
                      type="button" 
                      variant="secondary"
                      onClick={addUbo}
                    >
                      {t('compliance.addUbo')}
                    </Button>
                  </div>
                  
                  {ubos.map((ubo, index) => (
                    <Card key={index}>
                      <CardContent className="pt-6">
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                          <div className="space-y-2">
                            <Label>{t('compliance.name')}</Label>
                            <Input 
                              value={ubo.name}
                              onChange={(e) => updateUbo(index, 'name', e.target.value)}
                              required
                            />
                          </div>
                          <div className="space-y-2">
                            <Label>{t('compliance.dateOfBirth')}</Label>
                            <Input 
                              type="date"
                              value={ubo.dob}
                              onChange={(e) => updateUbo(index, 'dob', e.target.value)}
                              required
                            />
                          </div>
                          <div className="space-y-2">
                            <Label>{t('compliance.country')}</Label>
                            <Input 
                              value={ubo.country}
                              onChange={(e) => updateUbo(index, 'country', e.target.value)}
                              required
                            />
                          </div>
                        </div>
                        <Button 
                          type="button" 
                          variant="destructive"
                          className="mt-4"
                          onClick={() => removeUbo(index)}
                        >
                          {t('compliance.remove')}
                        </Button>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}

              <div className="flex justify-end gap-2">
                <Button type="submit">
                  {t('compliance.continue')}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          <Button variant="secondary" onClick={handleReset}>
            {t('compliance.back')}
          </Button>
          
          <ComplianceCheck 
            customer={{
              name: customerName,
              dob: customerDob || undefined,
              country: customerCountry,
              type: customerType
            }}
            directors={directors}
            ubos={ubos}
          />
        </div>
      )}
    </div>
  );
};

export default ComplianceCheckPage;
