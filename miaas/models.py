from django.db import models


class Tablespace(models.Model):
    name = models.CharField(max_length=30, db_index=True, db_tablespace="indexes")
    data = models.CharField(max_length=255, db_index=True)
    edges = models.ManyToManyField(to="self", db_tablespace="indexes")


class User(models.Model):
    user_id = models.CharField(max_length=30, primary_key=True)
    passwd = models.CharField(max_length=30)
    mobile = models.CharField(max_length=30)
    email = models.EmailField()
    join_date = models.DateField()
    deactivate_date = models.DateField()

    class Meta:
        db_tablespace = "tables"


class UserSession(models.Model):
    session_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    class Meta:
        db_tablespace = "tables"


class Patient(models.Model):
    user_id = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    gender = models.CharField(max_length=30)
    age = models.IntegerField()
    nationality = models.CharField(max_length=30)

    class Meta:
        db_tablespace = "tables"


class PatientProfile(models.Model):
    profile_id = models.AutoField(primary_key=True)
    patient_id = models.ForeignKey(Patient, on_delete=models.CASCADE)
    type = models.CharField(max_length=30)
    value = models.CharField(max_length=1000)
    timestamp = models.DateTimeField()
    status = models.CharField(max_length=30)

    class Meta:
        db_tablespace = "tables"


class Physician(models.Model):
    physician_id = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    field = models.CharField(max_length=30)
    score = models.FloatField()
    qualification = models.CharField(max_length=30)

    class Meta:
        db_tablespace = "tables"


class PhysicianProfile(models.Model):
    profile_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(Physician, on_delete=models.CASCADE)
    type = models.CharField(max_length=30)
    value = models.CharField(max_length=1000)

    class Meta:
        db_tablespace = "tables"


class MedicalImage(models.Model):
    mi_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=30)
    timestamp = models.DateTimeField()
    file_location = models.CharField(max_length=255)

    class Meta:
        db_tablespace = "tables"


class Interpretation(models.Model):
    mi_id = models.AutoField(primary_key=True)
    inpr_type = models.CharField(max_length=30)
    description = models.CharField(max_length=255)
    date = models.DateTimeField()

    class Meta:
        db_tablespace = "tables"


class Opinion(models.Model):
    user_id = models.ForeignKey(Physician, on_delete=models.CASCADE)
    mi_id = models.ForeignKey(MedicalImage, on_delete=models.CASCADE)
    opinion = models.CharField(max_length=255)
    date = models.DateTimeField()

    class Meta:
        db_tablespace = "tables"


if __name__ == '__main__':
    User.objects.all()
    pass
