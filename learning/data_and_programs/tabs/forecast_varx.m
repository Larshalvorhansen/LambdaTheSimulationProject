function Y = forecast_varx(Y0,horizon,X,p)
    
    % Define and estimate the model
    mod=varm(size(Y0,2),p);
    varx=estimate(mod,Y0(p+1:end,:),'Y0',Y0(1:p,:),'X',X(p+1:length(Y0),:));
    
    % Forecast the model
    Y=forecast(varx,horizon,Y0(end-p+1:end,:),'X',X(length(Y0)+1:length(Y0)+horizon,:));
end