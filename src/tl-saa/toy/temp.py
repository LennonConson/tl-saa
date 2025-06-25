stowable_cargo_capacity = {1:35000, 2:35000, 3:35000, 4:35000, 5:35000, 6:35000, 7:35000, # Bob Hope
                     8:36511, 9:36511, 10:36511, 11:36511, 12:36511, 13:36511, 14:36511, # Watson
                     15:26390, 16:26390, # Gordon
                     17:29029, 18:29029} # Shughart

# We need to have slightly more cargo space than possible outload
FACTOR = 1.0001*24000*20/sum(stowable_cargo_capacity.values())

scaled_stowable_cargo_capacity = {
    key: round(value * FACTOR)
    for key, value in stowable_cargo_capacity.items()
}

print(sum(stowable_cargo_capacity.values()))
print(24000*20/sum(scaled_stowable_cargo_capacity.values()))